import httpx
from app.core.config import settings

class RetailLLM:
    def __init__(self):
        self.api_key = settings.OLLAMA_API_KEY
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL

    async def prompt_summary(self, prompt: str) -> dict:
        if not self.api_key:
            return {"message": "Ollama Cloud API key is not configured."}
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    headers=headers,
                    timeout=60.0
                )
                result = response.json()
                return {"prompt": prompt, "summary": result.get("response", "")}
        except Exception as e:
            return {"error": str(e), "message": "Failed to generate summary"}
