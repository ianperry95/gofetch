from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.database import get_db
from app.models.schemas import ClusterMember, TopicCluster
from app.services.miniflux_client import miniflux

router = APIRouter()


@router.get("")
async def list_topics(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
) -> list[dict[str, Any]]:
    """List active topic clusters."""
    result = await db.execute(
        select(TopicCluster)
        .options(selectinload(TopicCluster.members))
        .order_by(TopicCluster.article_count.desc())
        .limit(limit)
    )
    clusters = result.scalars().all()

    return [
        {
            "id": c.id,
            "label": c.label,
            "summary": c.summary,
            "article_count": c.article_count,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "entry_ids": [m.miniflux_entry_id for m in c.members],
        }
        for c in clusters
    ]


@router.get("/{cluster_id}")
async def get_topic(
    cluster_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get a topic cluster with its articles."""
    result = await db.execute(
        select(TopicCluster)
        .options(selectinload(TopicCluster.members))
        .where(TopicCluster.id == cluster_id)
    )
    cluster = result.scalars().first()

    if not cluster:
        return {"error": "Topic not found"}

    # Fetch the actual entries from Miniflux
    entry_ids = [m.miniflux_entry_id for m in cluster.members]
    entries = []
    for entry_id in entry_ids:
        try:
            entry = await miniflux.get_entry(entry_id)
            entries.append(entry)
        except Exception:
            pass

    return {
        "id": cluster.id,
        "label": cluster.label,
        "summary": cluster.summary,
        "article_count": cluster.article_count,
        "created_at": cluster.created_at.isoformat() if cluster.created_at else None,
        "entries": entries,
    }
