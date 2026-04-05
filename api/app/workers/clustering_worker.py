"""Periodic worker that re-clusters recent articles into topics."""

import logging

from app.models.database import async_session
from app.routers.events import broadcast
from app.services.clustering_service import ClusteringService

logger = logging.getLogger(__name__)


async def clustering_worker(app) -> None:
    try:
        service = ClusteringService()
        async with async_session() as db:
            count = await service.run_clustering(db)
            if count > 0:
                logger.info("Clustering worker: created %d clusters", count)
                broadcast("clusters_updated", {"count": count})
    except Exception:
        logger.exception("Clustering worker failed")
