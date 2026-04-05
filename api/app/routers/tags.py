from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.schemas import ArticleTag, Tag

router = APIRouter()


class TagCreate(BaseModel):
    name: str
    color: str | None = None


class TagUpdate(BaseModel):
    name: str | None = None
    color: str | None = None


class TagArticles(BaseModel):
    miniflux_entry_ids: list[int]


@router.get("")
async def list_tags(db: AsyncSession = Depends(get_db)) -> list[dict[str, Any]]:
    result = await db.execute(
        select(
            Tag,
            func.count(ArticleTag.miniflux_entry_id).label("article_count"),
        )
        .outerjoin(ArticleTag, Tag.id == ArticleTag.tag_id)
        .group_by(Tag.id)
        .order_by(Tag.name)
    )
    return [
        {
            "id": tag.id,
            "name": tag.name,
            "color": tag.color,
            "article_count": count,
        }
        for tag, count in result.all()
    ]


@router.post("")
async def create_tag(
    body: TagCreate, db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    tag = Tag(name=body.name, color=body.color)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return {"id": tag.id, "name": tag.name, "color": tag.color}


@router.patch("/{tag_id}")
async def update_tag(
    tag_id: int, body: TagUpdate, db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    tag = await db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if body.name is not None:
        tag.name = body.name
    if body.color is not None:
        tag.color = body.color
    await db.commit()
    return {"id": tag.id, "name": tag.name, "color": tag.color}


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: int, db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    tag = await db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    await db.delete(tag)
    await db.commit()
    return {"status": "ok"}


@router.post("/{tag_id}/articles")
async def tag_articles(
    tag_id: int, body: TagArticles, db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    """Add tag to multiple articles."""
    tag = await db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    for entry_id in body.miniflux_entry_ids:
        existing = await db.execute(
            select(ArticleTag).where(
                ArticleTag.miniflux_entry_id == entry_id,
                ArticleTag.tag_id == tag_id,
            )
        )
        if not existing.scalars().first():
            db.add(ArticleTag(miniflux_entry_id=entry_id, tag_id=tag_id))
    await db.commit()
    return {"status": "ok"}


@router.delete("/{tag_id}/articles")
async def untag_articles(
    tag_id: int, body: TagArticles, db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    """Remove tag from multiple articles."""
    await db.execute(
        delete(ArticleTag).where(
            ArticleTag.tag_id == tag_id,
            ArticleTag.miniflux_entry_id.in_(body.miniflux_entry_ids),
        )
    )
    await db.commit()
    return {"status": "ok"}


@router.get("/{tag_id}/entries")
async def get_tag_entries(
    tag_id: int, db: AsyncSession = Depends(get_db)
) -> list[int]:
    """Get all entry IDs with this tag."""
    result = await db.execute(
        select(ArticleTag.miniflux_entry_id).where(ArticleTag.tag_id == tag_id)
    )
    return [row[0] for row in result.all()]


@router.get("/entry/{entry_id}")
async def get_entry_tags(
    entry_id: int, db: AsyncSession = Depends(get_db)
) -> list[dict[str, Any]]:
    """Get all tags for an entry."""
    result = await db.execute(
        select(Tag)
        .join(ArticleTag, Tag.id == ArticleTag.tag_id)
        .where(ArticleTag.miniflux_entry_id == entry_id)
    )
    return [{"id": t.id, "name": t.name, "color": t.color} for t in result.scalars().all()]
