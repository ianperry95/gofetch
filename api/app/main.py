import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.embeddings.factory import create_embedding_provider
from app.models.database import Base, engine
from app.routers import collections, events, feed, interactions, saved_views, settings, tags, topics, webhooks
from app.services.embedding_service import EmbeddingService
from app.services.pipeline import Pipeline
from app.workers.scheduler import start_scheduler, stop_scheduler

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    # Startup
    logger.info("Starting GoFetch API...")

    # Ensure all tables exist (safe for first run; no-op if tables already exist)
    # Import all models so Base.metadata is populated
    import app.models.schemas  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ensured.")

    provider = create_embedding_provider()
    embedding_service = EmbeddingService(provider)
    application.state.pipeline = Pipeline(embedding_service)
    application.state.embedding_provider = provider

    start_scheduler(application)

    yield

    # Shutdown
    stop_scheduler()
    await provider.close()
    logger.info("GoFetch API stopped.")


app = FastAPI(title="GoFetch", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(feed.router, prefix="/api/feed", tags=["feed"])
app.include_router(topics.router, prefix="/api/topics", tags=["topics"])
app.include_router(tags.router, prefix="/api/tags", tags=["tags"])
app.include_router(collections.router, prefix="/api/collections", tags=["collections"])
app.include_router(saved_views.router, prefix="/api/saved-views", tags=["saved-views"])
app.include_router(interactions.router, prefix="/api/interactions", tags=["interactions"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(events.router, prefix="/api/events", tags=["events"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}
