"""Periodic worker that recomputes article ranking scores."""

import logging

from app.models.database import async_session
from app.services.ranking_service import RankingService

logger = logging.getLogger(__name__)


async def ranking_worker(app) -> None:
    try:
        service = RankingService()
        async with async_session() as db:
            count = await service.rank_entries(db)
            if count > 0:
                logger.info("Ranking worker: scored %d entries", count)
    except Exception:
        logger.exception("Ranking worker failed")
