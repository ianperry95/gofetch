"""Catch-up worker: polls Miniflux for entries missing from our embeddings table.

Runs every N minutes as a safety net for missed webhooks.
"""

import logging

from sqlalchemy import func, select

from app.models.database import async_session
from app.models.schemas import ArticleEmbedding
from app.services.miniflux_client import miniflux
from app.services.pipeline import Pipeline

logger = logging.getLogger(__name__)

BATCH_SIZE = 100


async def catchup_sync(app) -> None:
    """Fetch recent entries from Miniflux and embed any we've missed."""
    pipeline: Pipeline = app.state.pipeline

    try:
        async with async_session() as db:
            # Find the highest miniflux_entry_id we've embedded
            result = await db.execute(
                select(func.max(ArticleEmbedding.miniflux_entry_id))
            )
            max_id = result.scalar() or 0

        # Fetch entries from Miniflux after our last known ID
        data = await miniflux.get_entries(
            limit=BATCH_SIZE,
            order="id",
            direction="asc",
            after_entry_id=max_id if max_id > 0 else None,
        )
        entries = data.get("entries", []) or []

        if not entries:
            logger.debug("Catch-up: no new entries since id=%d", max_id)
            return

        logger.info("Catch-up: found %d entries after id=%d", len(entries), max_id)

        async with async_session() as db:
            await pipeline.process_entries(db, entries)

    except Exception:
        logger.exception("Catch-up sync failed")
