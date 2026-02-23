"""
FastAPI Application Entry Point.
Sets up CORS, includes routes, initializes DB on startup.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="Interview Prep Trainer",
    description="AI-powered interview preparation platform — generates questions, grades answers, provides hints and feedback",
    version="2.0.0",
)

# CORS — allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://64.226.111.25:3000",
        "http://64.226.111.25",
        "http://164.92.183.143:3000",
        "http://164.92.183.143",
        "http://164.92.183.143:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.on_event("startup")
def on_startup():
    """Initialize database tables on startup."""
    logging.info("Initializing database...")
    init_db()
    logging.info("Database initialized successfully.")
