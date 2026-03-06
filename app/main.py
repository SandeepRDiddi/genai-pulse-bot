"""
GenAI Pulse Bot - Main FastAPI Application
Tracks latest GenAI developments across Arxiv, HuggingFace, Reddit, and Tech News.
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.routes import router as api_router
from app.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 GenAI Pulse Bot starting up...")
    await init_db()
    yield
    logger.info("🛑 GenAI Pulse Bot shutting down...")


app = FastAPI(
    title="GenAI Pulse Bot",
    description="Stay up to date with the latest in Generative AI",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/", include_in_schema=False)
async def dashboard():
    return FileResponse("app/dashboard/index.html")
