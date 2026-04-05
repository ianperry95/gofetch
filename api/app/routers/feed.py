from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.schemas import ArticleScore
from app.services.miniflux_client import miniflux

router = APIRouter()


@router.get("")
async def get_feed(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort: str = Query("ranked", pattern="^(ranked|newest|oldest)$"),
    feed_id: int | None = Query(None),
    status: str = Query("unread", pattern="^(unread|read|removed)$"),
    hide_duplicates: bool = Query(True),
) -> dict[str, Any]:
    """Get the feed, optionally ranked by AI scores."""
    if sort == "ranked":
        return await _get_ranked_feed(db, limit, offset, feed_id, status, hide_duplicates)

    direction = "desc" if sort == "newest" else "asc"
    result = await miniflux.get_entries(
        status=status,
        limit=limit,
        offset=offset,
        direction=direction,
        feed_id=feed_id,
    )

    entries = result.get("entries", []) or []
    if hide_duplicates:
        entries = await _filter_duplicates(db, entries)

    return {"entries": entries, "total": result.get("total", 0)}


async def _get_ranked_feed(
    db: AsyncSession,
    limit: int,
    offset: int,
    feed_id: int | None,
    status: str,
    hide_duplicates: bool,
) -> dict[str, Any]:
    """Fetch entries and sort by precomputed AI scores."""
    # Fetch a larger batch from Miniflux to rank from
    result = await miniflux.get_entries(
        status=status, limit=min(limit * 3, 200), offset=0, feed_id=feed_id
    )
    entries = result.get("entries", []) or []

    if not entries:
        return {"entries": [], "total": 0}

    entry_ids = [e["id"] for e in entries]
    scores_result = await db.execute(
        select(ArticleScore).where(ArticleScore.miniflux_entry_id.in_(entry_ids))
    )
    scores = {s.miniflux_entry_id: s for s in scores_result.scalars().all()}

    # Annotate entries with scores
    for entry in entries:
        score = scores.get(entry["id"])
        entry["_score"] = score.final_score if score else 0.0
        entry["_is_duplicate"] = score.is_duplicate if score else False
        entry["_cluster_id"] = score.cluster_id if score else None

    if hide_duplicates:
        entries = [e for e in entries if not e.get("_is_duplicate", False)]

    entries.sort(key=lambda e: e.get("_score", 0.0), reverse=True)
    paginated = entries[offset : offset + limit]

    return {"entries": paginated, "total": len(entries)}


async def _filter_duplicates(db: AsyncSession, entries: list[dict]) -> list[dict]:
    """Remove duplicate entries based on precomputed scores."""
    if not entries:
        return entries

    entry_ids = [e["id"] for e in entries]
    scores_result = await db.execute(
        select(ArticleScore).where(
            ArticleScore.miniflux_entry_id.in_(entry_ids), ArticleScore.is_duplicate.is_(True)
        )
    )
    duplicate_ids = {s.miniflux_entry_id for s in scores_result.scalars().all()}

    return [e for e in entries if e["id"] not in duplicate_ids]


@router.get("/feeds")
async def get_feeds() -> list[dict[str, Any]]:
    """List all feeds from Miniflux."""
    return await miniflux.get_feeds()


@router.get("/categories")
async def get_categories() -> list[dict[str, Any]]:
    """List all categories from Miniflux."""
    return await miniflux.get_categories()


@router.get("/entry/{entry_id}")
async def get_entry(entry_id: int) -> dict[str, Any]:
    """Get a single entry by ID."""
    return await miniflux.get_entry(entry_id)


@router.put("/entries/status")
async def update_entries_status(entry_ids: list[int], status: str) -> dict[str, str]:
    """Update read status of entries in Miniflux."""
    await miniflux.update_entries(entry_ids, status)
    return {"status": "ok"}


@router.put("/entry/{entry_id}/bookmark")
async def toggle_bookmark(entry_id: int) -> dict[str, str]:
    """Toggle bookmark status in Miniflux."""
    await miniflux.toggle_bookmark(entry_id)
    return {"status": "ok"}


@router.get("/search")
async def search(q: str = Query(..., min_length=1), limit: int = Query(50)) -> dict[str, Any]:
    """Search entries via Miniflux."""
    return await miniflux.search_entries(q, limit=limit)
