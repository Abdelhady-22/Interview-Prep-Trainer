"""
HealthService — Checks connectivity to all dependencies.
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.integrations.ollama_client import ollama_client

logger = logging.getLogger(__name__)


class HealthService:
    """Checks the health of all dependencies."""

    def __init__(self, db: Session):
        self.db = db

    async def check_all(self) -> dict:
        """Check backend, database, and Ollama health."""
        result = {
            "backend": "ok",
            "database": "error",
            "ollama": "error",
        }

        # Check database
        try:
            self.db.execute(text("SELECT 1"))
            result["database"] = "ok"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            result["database"] = f"error: {str(e)}"

        # Check Ollama
        try:
            is_healthy = await ollama_client.is_healthy()
            result["ollama"] = "ok" if is_healthy else "unreachable"
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            result["ollama"] = f"error: {str(e)}"

        return result
