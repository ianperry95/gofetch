import asyncio
import hashlib
import hmac
import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.database import get_db
from app.routers.events import broadcast
from app.services.pipeline import Pipeline

logger = logging.getLogger(__name__)

router = APIRouter()


def _verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify Miniflux webhook HMAC-SHA256 signature."""
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def _get_pipeline(request: Request) -> Pipeline:
    return request.app.state.pipeline


@router.post("/miniflux")
async def miniflux_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    pipeline: Pipeline = Depends(_get_pipeline),
    x_miniflux_event_type: str = Header(...),
    x_miniflux_signature: str = Header(...),
) -> dict[str, str]:
    """Receive webhook events from Miniflux."""
    body = await request.body()

    if settings.miniflux_webhook_secret:
        if not _verify_signature(body, x_miniflux_signature, settings.miniflux_webhook_secret):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = await request.json()

    if x_miniflux_event_type == "new_entries":
        entries = payload.get("entries", [])
        logger.info("Received %d new entries via webhook", len(entries))

        # Notify SSE clients about new articles
        broadcast("new_entries", {"count": len(entries)})

        # Process in background so the webhook returns quickly
        asyncio.create_task(_process_entries(pipeline, entries))

    elif x_miniflux_event_type == "save_entry":
        logger.info("Received save_entry webhook event")
    else:
        logger.warning("Unknown webhook event type: %s", x_miniflux_event_type)

    return {"status": "ok"}


async def _process_entries(pipeline: Pipeline, entries: list[dict]) -> None:
    """Process entries in the background."""
    from app.models.database import async_session

    try:
        async with async_session() as db:
            await pipeline.process_entries(db, entries)
    except Exception:
        logger.exception("Failed to process webhook entries")
