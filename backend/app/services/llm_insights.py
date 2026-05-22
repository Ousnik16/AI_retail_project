import httpx
import json
import re
from app.core.config import settings
from app.db.database import get_collection
from app.services.analytics import AnalyticsService
from app.services.sentiment import SentimentService
from app.utils.ollama import ollama_api_url

class LLMInsightsService:
    @staticmethod
    def _extract_product_ids(obj):
        ids = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k.lower() in ("product_id", "productid", "id", "sku") and isinstance(v, (str, int)):
                    ids.append(str(v))
                else:
                    ids.extend(LLMInsightsService._extract_product_ids(v))
        elif isinstance(obj, list):
            for item in obj:
                ids.extend(LLMInsightsService._extract_product_ids(item))
        # return unique, non-empty ids
        return list(dict.fromkeys([i for i in ids if i]))

    @staticmethod
    def _extract_model_text(result: dict) -> str:
        # Try known keys from different LLM providers
        if not result:
            return ""
        for key in ("response", "output", "text", "content"):
            if key in result and isinstance(result[key], str) and result[key].strip():
                return result[key]

        # Choices / results arrays
        if isinstance(result.get("choices"), list) and result["choices"]:
            parts = []
            for c in result["choices"]:
                if isinstance(c, dict):
                    # common shape: {message: {content: '...'}}
                    msg = c.get("message") or c.get("delta") or c
                    if isinstance(msg, dict):
                        content = msg.get("content") or msg.get("text")
                        if content:
                            parts.append(content)
                    else:
                        text = c.get("text")
                        if text:
                            parts.append(text)
            return "\n".join(parts).strip()

        if isinstance(result.get("results"), list) and result["results"]:
            parts = []
            for r in result["results"]:
                if isinstance(r, dict):
                    txt = r.get("text") or r.get("content")
                    if txt:
                        parts.append(txt)
            return "\n".join(parts).strip()

        return ""

    @staticmethod
    def _parse_llm_json(text: str) -> dict:
        try:
            return json.loads(text)
        except Exception:
            pass

        match = re.search(r"(\{.*\})", text, flags=re.S)
        if not match:
            return {}

        try:
            return json.loads(match.group(1))
        except Exception:
            return {}

    @staticmethod
    def _response(question: str, summary: str, context: dict, source: str, actions=None, warning: str | None = None) -> dict:
        product_ids = LLMInsightsService._extract_product_ids({"summary": summary, "actions": actions or []})
        response = {
            "question": question,
            "summary": summary,
            "insight": summary,
            "actions": actions or [],
            "product_ids": product_ids,
            "context": context,
            "source": source,
        }
        if warning:
            response["warning"] = warning
        return response

    @staticmethod
    async def _retail_context() -> dict:
        try:
            products = []
            async for product in get_collection("products").find({}).limit(8):
                products.append(
                    {
                        "sku": product.get("sku"),
                        "name": product.get("name"),
                        "category": product.get("category"),
                        "price": product.get("price"),
                        "inventory_quantity": product.get("inventory_quantity"),
                    }
                )
        except Exception:
            products = []

        dashboard = await AnalyticsService.dashboard_overview()
        return {
            "sales": {
                "total_sales": dashboard.get("total_sales", 0),
                "order_count": dashboard.get("order_count", 0),
                "active_users": dashboard.get("active_users", 0),
            },
            "top_selling_products": dashboard.get("top_selling_products", [])[:5],
            "basket_analysis": dashboard.get("basket_analysis", [])[:5],
            "customer_segments": dashboard.get("customer_insights", [])[:5],
            "recommendation_performance": dashboard.get("recommendation_performance", {}),
            "inventory_snapshot": products,
        }

    @staticmethod
    def _fallback_insight(question: str, context: dict) -> str:
        sales = context["sales"]
        top_products = context.get("top_selling_products", [])
        baskets = context.get("basket_analysis", [])
        segments = context.get("customer_segments", [])
        inventory = context.get("inventory_snapshot", [])
        top_product = top_products[0]["name"] if top_products and top_products[0].get("name") else "the current top product"
        top_basket = " + ".join(baskets[0]["products"]) if baskets else "laptop and accessory bundles"
        segment = segments[0].get("persona", "high-intent shoppers") if segments else "high-intent shoppers"
        low_stock = sorted(
            [item for item in inventory if item.get("inventory_quantity") is not None],
            key=lambda item: item.get("inventory_quantity", 999999),
        )[:3]
        low_stock_text = ", ".join(
            f"{item.get('name') or item.get('sku')} ({item.get('inventory_quantity')} left)" for item in low_stock
        ) or "no low-stock products in the current snapshot"
        q = question.lower()

        if any(term in q for term in ("stock", "inventory", "shortage", "restock")):
            return (
                f"Inventory answer for: {question}\n\n"
                f"Products to watch: {low_stock_text}.\n\n"
                f"Sales signal: {top_product} is the strongest demand signal from current transactions. "
                "Prioritize restocking low inventory items that also appear in top-selling or basket combinations.\n\n"
                "Recommended action: review supplier lead times, raise reorder quantities for fast-moving low-stock items, "
                "and avoid heavy promotion on products with constrained stock."
            )

        if any(term in q for term in ("segment", "customer", "target", "audience")):
            return (
                f"Customer targeting answer for: {question}\n\n"
                f"Best segment to act on: {segment}. This segment is visible in the current customer analytics context.\n\n"
                f"Offer angle: connect the segment to {top_basket} because basket signals show useful cross-sell behavior.\n\n"
                "Recommended action: send a focused offer to this segment, personalize the bundle by preferred categories, "
                "and compare conversion against a control group."
            )

        if any(term in q for term in ("bundle", "product", "performance", "campaign")):
            return (
                f"Product performance answer for: {question}\n\n"
                f"Lead product signal: {top_product}. Pair it with observed basket behavior such as {top_basket}.\n\n"
                f"Inventory guardrail: check {low_stock_text} before launching a promotion.\n\n"
                "Recommended action: create a bundle campaign around the leading product, attach accessories with healthy stock, "
                "and monitor basket size plus conversion."
            )

        return (
            f"Retail intelligence response for: {question}\n\n"
            f"Sales summary: ${float(sales.get('total_sales', 0)):.2f} across {sales.get('order_count', 0)} orders "
            f"with {sales.get('active_users', 0)} active customer segments.\n\n"
            f"Customer intelligence: the strongest visible segment is {segment}. Prioritize category bundles and targeted offers "
            f"for shoppers with repeated purchases.\n\n"
            f"Product performance: {top_product} is the lead product signal. Monitor its inventory and attach complementary items "
            f"to improve basket size.\n\n"
            f"Basket opportunity: {top_basket} appears as a useful shopping combination. Promote it as a bundle and watch conversion.\n\n"
            "Recommended action: refresh demand forecasts for the top products, check low-stock items, and generate personalized offers "
            "for customers whose browsing history matches the best-performing baskets."
        )

    @staticmethod
    def _fallback_actions(context: dict):
        actions = []
        top_products = context.get("top_selling_products", [])
        if top_products:
            top = top_products[0]
            pid = top.get("product_id") or top.get("sku") or top.get("id")
            actions.append({
                "type": "add_to_cart",
                "label": f"Buy {top.get('name', pid)}",
                "payload": {"product_id": pid, "name": top.get("name"), "unit_price": top.get("price", 0)},
            })

        baskets = context.get("basket_analysis", [])
        if baskets:
            # suggest promoting first basket
            actions.append({"type": "promote_bundle", "label": "Create bundle campaign", "payload": {"products": baskets[0].get("products", [])}})

        return actions

    @staticmethod
    def _customer_fallback_insight(question: str, context: dict) -> str:
        top_products = context.get("top_selling_products", [])
        baskets = context.get("basket_analysis", [])
        top_product = top_products[0].get("name") if top_products else "a popular product"
        basket = " + ".join(baskets[0].get("products", [])) if baskets else "a main item with a useful accessory"
        return (
            f"Shopping answer for: {question}\n\n"
            f"Good place to start: consider {top_product} if it matches what you are shopping for right now.\n\n"
            f"Helpful pairing: customers often buy {basket}, so check whether the add-on actually solves your need before adding it.\n\n"
            "Next step: compare price, category, rating, and whether the item fits your current use case. "
            "For personal recommendations, use your Recommendations page after you have more order history."
        )

    @staticmethod
    async def generate_insight(question: str, user: dict | None = None):
        context = await LLMInsightsService._retail_context()
        is_customer = user and "admin" not in user.get("roles", [])
        blocked_terms = ("revenue", "sales", "stock", "inventory", "shortage", "segment", "business", "admin", "campaign", "profit")
        if is_customer and any(term in question.lower() for term in blocked_terms):
            summary = (
                "I can help with shopping questions such as product fit, category choices, comparisons, and what to consider before buying. "
                "Business, inventory, sales, and admin questions are available in the admin workspace."
            )
            return LLMInsightsService._response(question, summary, {}, "customer-guardrail", [])

        if not settings.OLLAMA_API_KEY:
            if is_customer:
                return LLMInsightsService._response(
                    question,
                    LLMInsightsService._customer_fallback_insight(question, context),
                    {},
                    "dynamic-fallback",
                    [],
                )
            return LLMInsightsService._response(
                question,
                LLMInsightsService._fallback_insight(question, context),
                context,
                "dynamic-fallback",
                LLMInsightsService._fallback_actions(context),
            )
        
        try:
            # Ask the LLM to return a strict JSON object with a short `summary` and `actions` array
            if is_customer:
                prompt = (
                    "You are a shopping assistant for a retail customer. Answer only customer shopping questions using general product and category context. "
                    "Do not provide business, revenue, inventory, stock, segmentation, campaign, or admin recommendations. "
                    "Return ONLY JSON with keys `summary` (string) and `actions` (array). Keep actions empty unless it is a simple shopping action.\n\n"
                    f"Product context JSON: {json.dumps({'top_products': context.get('top_selling_products', []), 'baskets': context.get('basket_analysis', [])})}\n\n"
                    f"Customer question: {question}"
                )
            else:
                prompt = (
                "You are an AI retail intelligence analyst. Use the supplied JSON context to answer the user's question. "
                "Return ONLY a JSON object with these keys: `summary` (string), `actions` (array of {type, label, payload}), "
                "and optional `notes` (string). Do NOT include any extra explanatory text outside the JSON. "
                "Use numbers only from the provided context and do not hallucinate exact metrics.\n\n"
                f"Retail context JSON: {json.dumps(context)}\n\n"
                f"User question: {question}"
                )
            headers = {
                "Authorization": f"Bearer {settings.OLLAMA_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    ollama_api_url(settings.OLLAMA_BASE_URL, "generate"),
                    json=payload,
                    headers=headers,
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                text = LLMInsightsService._extract_model_text(result) or ""
                parsed = LLMInsightsService._parse_llm_json(text)
                if parsed:
                    summary = parsed.get("summary") or parsed.get("insight") or text
                    actions = parsed.get("actions") if isinstance(parsed.get("actions"), list) else []
                    return LLMInsightsService._response(question, summary, {} if is_customer else context, "ollama", actions if not is_customer else [])

                # If no JSON was returned, return only summary (raw text) and empty product list
                return LLMInsightsService._response(
                    question,
                    text or (LLMInsightsService._customer_fallback_insight(question, context) if is_customer else LLMInsightsService._fallback_insight(question, context)),
                    {} if is_customer else context,
                    "ollama",
                    [] if is_customer else LLMInsightsService._fallback_actions(context),
                )
        except Exception as e:
            return LLMInsightsService._response(
                question,
                LLMInsightsService._customer_fallback_insight(question, context) if is_customer else LLMInsightsService._fallback_insight(question, context),
                {} if is_customer else context,
                "dynamic-fallback",
                [] if is_customer else LLMInsightsService._fallback_actions(context),
                f"LLM request failed: {e}",
            )

    @staticmethod
    async def generate_review_insight(question: str, user_id: str | None = None):
        # Build review-focused context
        context = await LLMInsightsService._retail_context()
        sentiment = await SentimentService.analyze_reviews(user_id)
        review_list = sentiment.get("sentiment", [])
        products_by_id = {}
        for product in context.get("inventory_snapshot", []):
            if product.get("sku"):
                products_by_id[product["sku"]] = product

        counts = {"positive": 0, "negative": 0}
        by_product = {}
        samples = []
        for r in review_list:
            lbl = r.get("label", "POSITIVE")
            if lbl == "POSITIVE":
                counts["positive"] += 1
            else:
                counts["negative"] += 1
            pid = r.get("product_id")
            product = products_by_id.get(pid, {})
            by_product.setdefault(
                pid,
                {
                    "name": product.get("name") or pid,
                    "stock": product.get("inventory_quantity"),
                    "positive": 0,
                    "negative": 0,
                    "ratings": [],
                },
            )
            by_product[pid]["positive" if lbl == "POSITIVE" else "negative"] += 1
            if r.get("rating"):
                by_product[pid]["ratings"].append(r.get("rating"))
            if len(samples) < 6:
                samples.append({
                    "product_id": pid,
                    "label": lbl,
                    "confidence": r.get("score", 0),
                    "review_text": r.get("review_text", "")[:220],
                    "rating": r.get("rating"),
                })

        review_context = {"summary": counts, "by_product": by_product, "samples": samples}
        review_context["attention_products"] = [
            {"product_id": pid, **data}
            for pid, data in sorted(
                by_product.items(),
                key=lambda item: (item[1]["negative"], -(item[1].get("stock") or 0)),
                reverse=True,
            )
            if data["negative"] > 0 or (data.get("stock") is not None and data["stock"] < 45)
        ][:5]

        fallback_actions = [
            {
                "type": "review_stock",
                "label": f"Review stock for {item['name']}",
                "payload": {
                    "product_id": item["product_id"],
                    "current_stock": item.get("stock"),
                    "negative_reviews": item.get("negative", 0),
                },
            }
            for item in review_context["attention_products"][:3]
        ]

        # Ask LLM for business insights focused on reviews
        if not settings.OLLAMA_API_KEY:
            attention = review_context["attention_products"]
            if attention:
                product_lines = "\n".join(
                    f"- {item['name']}: {item['negative']} negative review(s), {item['positive']} positive review(s), stock {item.get('stock', 'unknown')}"
                    for item in attention[:3]
                )
            else:
                product_lines = "- No product has enough negative sentiment to require immediate intervention."
            insight_text = (
                f"Review intelligence answer for: {question}\n\n"
                f"Sentiment summary: {counts['positive']} positive and {counts['negative']} negative review(s).\n\n"
                f"Products needing attention:\n{product_lines}\n\n"
                "Recommended admin actions: inspect products with negative feedback before promoting them, update stock for well-reviewed "
                "items with low inventory, and use repeated complaint themes to adjust quality checks, product copy, or supplier follow-up."
            )
            return LLMInsightsService._response(question, insight_text, {**context, "reviews": review_context}, "dynamic-fallback", fallback_actions)

        try:
            prompt = (
                "You are an AI retail analyst. Using the JSON context of aggregated review sentiment and review samples, "
                "provide a concise business insight that highlights product issues, suggested operational actions (e.g., returns review, prioritize QC, bundle replacements), "
                "and at most 3 actionable recommendations formatted as JSON {summary, actions:[{type,label,payload}]}. Do not hallucinate specifics.\n\n"
                f"Context JSON: {json.dumps({**context, 'reviews': review_context})}\n\n"
                f"User question: {question}"
            )
            headers = {
                "Authorization": f"Bearer {settings.OLLAMA_API_KEY}",
                "Content-Type": "application/json",
            }
            payload = {"model": settings.OLLAMA_MODEL, "prompt": prompt, "stream": False}
            async with httpx.AsyncClient() as client:
                response = await client.post(ollama_api_url(settings.OLLAMA_BASE_URL, "generate"), json=payload, headers=headers, timeout=60.0)
                response.raise_for_status()
                result = response.json()
                text = LLMInsightsService._extract_model_text(result) or ""
                parsed = LLMInsightsService._parse_llm_json(text)
                if parsed:
                    summary = parsed.get("summary") or parsed.get("insight") or text
                    actions = parsed.get("actions") if isinstance(parsed.get("actions"), list) else fallback_actions
                    return LLMInsightsService._response(question, summary, {**context, "reviews": review_context}, "ollama", actions)
                return LLMInsightsService._response(question, text or "No insight generated.", {**context, "reviews": review_context}, "ollama", fallback_actions)
        except Exception as e:
            attention = review_context["attention_products"]
            product_lines = "\n".join(
                f"- {item['name']}: {item['negative']} negative review(s), {item['positive']} positive review(s), stock {item.get('stock', 'unknown')}"
                for item in attention[:3]
            ) if attention else "- No product has enough negative sentiment to require immediate intervention."
            insight_text = (
                f"Review intelligence answer for: {question}\n\n"
                f"Sentiment summary: {counts['positive']} positive and {counts['negative']} negative review(s).\n\n"
                f"Products needing attention:\n{product_lines}\n\n"
                "Recommended admin actions: inspect products with negative feedback before promoting them, update stock for well-reviewed "
                "items with low inventory, and use repeated complaint themes to adjust quality checks, product copy, or supplier follow-up."
            )
            return LLMInsightsService._response(
                question,
                insight_text,
                {**context, "reviews": review_context},
                "dynamic-fallback",
                fallback_actions,
                f"LLM request failed: {e}",
            )
