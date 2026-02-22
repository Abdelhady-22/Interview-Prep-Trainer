import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class OllamaClient:
    """Integration layer for communicating with the Ollama API."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.timeout = 120.0  # 2 minutes for LLM generation

    async def generate(self, prompt: str, system: str = "", model: str = None) -> str:
        """
        Send a prompt to Ollama and return the generated text.
        Uses the /api/generate endpoint with stream=false.
        """
        model = model or settings.OLLAMA_MODEL
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
        except httpx.TimeoutException:
            logger.error(f"Ollama request timed out after {self.timeout}s")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Ollama request failed: {str(e)}")
            raise

    async def is_healthy(self) -> bool:
        """Check if Ollama is reachable."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False


ollama_client = OllamaClient()
