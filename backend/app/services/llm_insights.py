import httpx
from app.core.config import settings
from app.db.database import get_collection
from app.services.analytics import AnalyticsService
from app.utils.ollama import ollama_api_url

class LLMInsightsService:
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
        top_product = top_products[0]["name"] if top_products and top_products[0].get("name") else "the current top product"
        top_basket = " + ".join(baskets[0]["products"]) if baskets else "laptop and accessory bundles"
        segment = segments[0].get("persona", "high-intent shoppers") if segments else "high-intent shoppers"

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
    async def generate_insight(question: str):
        context = await LLMInsightsService._retail_context()
        if not settings.OLLAMA_API_KEY:
            return {
                "question": question,
                "insight": LLMInsightsService._fallback_insight(question, context),
                "context": context,
                "source": "dynamic-fallback",
            }
        
        try:
            prompt = (
                "You are an AI retail intelligence analyst. Use the supplied JSON context to answer the user's question "
                "with concise sales summaries, customer intelligence, product performance notes, and operational actions. "
                "Do not invent numbers outside the context.\n\n"
                f"Retail context: {context}\n\n"
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
                return {
                    "question": question,
                    "insight": result.get("response", "") or LLMInsightsService._fallback_insight(question, context),
                    "context": context,
                    "source": "ollama",
                }
        except Exception as e:
            return {
                "question": question,
                "insight": LLMInsightsService._fallback_insight(question, context),
                "context": context,
                "source": "dynamic-fallback",
                "warning": f"LLM request failed: {e}",
            }
