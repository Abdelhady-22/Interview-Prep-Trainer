import httpx
import logging
import os
import uuid
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)

# Directory to save raw LLM responses
LLM_LOG_DIR = os.environ.get("LLM_LOG_DIR", "/app/llm_logs")
os.makedirs(LLM_LOG_DIR, exist_ok=True)

# Common LLM noise patterns to strip before JSON parsing
LLM_NOISE_PREFIXES = [
    "my best complete final answer to the task.",
    "Your final answer must be the great and the most complete as possible, it must be outcome described.",
    "Here is my final answer:",
    "Final Answer:",
    "Here is the JSON:",
]


def strip_llm_noise(text: str) -> str:
    """Strip common LLM boilerplate noise from responses before JSON parsing."""
    cleaned = text.strip()
    # Remove noise prefixes (case-insensitive)
    for prefix in LLM_NOISE_PREFIXES:
        if cleaned.lower().startswith(prefix.lower()):
            cleaned = cleaned[len(prefix):].strip()
    # Strip markdown code fences
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()

def save_llm_response(prefix: str, prompt: str, response: str, system: str = "", model: str = ""):
    """Save a raw LLM response to a timestamped file."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        short_id = uuid.uuid4().hex[:8]
        filename = f"{prefix}_{timestamp}_{short_id}.txt"
        filepath = os.path.join(LLM_LOG_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"=== LLM Response Log ===\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Model: {model}\n")
            f.write(f"Prefix: {prefix}\n")
            f.write(f"\n--- SYSTEM ---\n{system}\n")
            f.write(f"\n--- PROMPT ---\n{prompt}\n")
            f.write(f"\n--- RAW RESPONSE ---\n{response}\n")

        logger.info(f"LLM response saved to: {filepath}")
    except Exception as e:
        logger.warning(f"Failed to save LLM response: {e}")


class OllamaClient:
    """Integration layer for communicating with the Ollama API."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.timeout = 120.0  # 2 minutes for LLM generation

    async def generate(self, prompt: str, system: str = "", model: str = None, temperature: float = 0.1) -> str:
        """
        Send a prompt to Ollama and return the generated text.
        Uses the /api/generate endpoint with stream=false.
        """
        model = model or settings.OLLAMA_MODEL
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
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
                raw_response = data.get("response", "")
                save_llm_response(
                    prefix="single",
                    prompt=prompt,
                    response=raw_response,
                    system=system,
                    model=model,
                )
                return raw_response
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
