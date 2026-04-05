import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


def start_scheduler(app) -> None:
    global _scheduler
    _scheduler = AsyncIOScheduler()

    from app.workers.catchup_sync import catchup_sync
    from app.workers.clustering_worker import clustering_worker
    from app.workers.ranking_worker import ranking_worker

    _scheduler.add_job(
        catchup_sync,
        "interval",
        minutes=settings.catchup_poll_interval_minutes,
        args=[app],
        id="catchup_sync",
        name="Catch-up sync from Miniflux",
        max_instances=1,
    )

    _scheduler.add_job(
        ranking_worker,
        "interval",
        minutes=settings.ranking_interval_minutes,
        args=[app],
        id="ranking_worker",
        name="Recompute article ranking scores",
        max_instances=1,
    )

    _scheduler.add_job(
        clustering_worker,
        "interval",
        minutes=settings.clustering_interval_minutes,
        args=[app],
        id="clustering_worker",
        name="Re-cluster articles into topics",
        max_instances=1,
    )

    _scheduler.start()
    logger.info(
        "Scheduler started: catch-up=%dm, ranking=%dm, clustering=%dm",
        settings.catchup_poll_interval_minutes,
        settings.ranking_interval_minutes,
        settings.clustering_interval_minutes,
    )


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
