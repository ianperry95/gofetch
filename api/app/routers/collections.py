from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.database import get_db
from app.models.schemas import Collection, CollectionItem

router = APIRouter()


class CollectionCreate(BaseModel):
    name: str
    description: str | None = None
    icon: str | None = None
    is_smart: bool = False
    filter_json: dict | None = None


class CollectionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    icon: str | None = None
    filter_json: dict | None = None
    sort_order: int | None = None


class CollectionArticles(BaseModel):
    miniflux_entry_ids: list[int]


@router.get("")
async def list_collections(db: AsyncSession = Depends(get_db)) -> list[dict[str, Any]]:
    result = await db.execute(
        select(Collection)
        .options(selectinload(Collection.items))
        .order_by(Collection.sort_order, Collection.name)
    )
    collections = result.scalars().all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "icon": c.icon,
            "is_smart": c.is_smart,
            "filter_json": c.filter_json,
            "sort_order": c.sort_order,
            "article_count": len(c.items),
        }
        for c in collections
    ]


@router.post("")
async def create_collection(
    body: CollectionCreate, db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    collection = Collection(
        name=body.name,
        description=body.description,
        icon=body.icon,
        is_smart=body.is_smart,
        filter_json=body.filter_json,
    )
    db.add(collection)
    await db.commit()
    await db.refresh(collection)
    return {
        "id": collection.id,
        "name": collection.name,
        "description": collection.description,
        "icon": collection.icon,
        "is_smart": collection.is_smart,
    }


@router.get("/{collection_id}")
async def get_collection(
    collection_id: int, db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    result = await db.execute(
        select(Collection)
        .options(selectinload(Collection.items))
        .where(Collection.id == collection_id)
    )
    c = result.scalars().first()
    if not c:
        raise HTTPException(status_code=404, detail="Collection not found")
    return {
        "id": c.id,
        "name": c.name,
        "description": c.description,
        "icon": c.icon,
        "is_smart": c.is_smart,
        "filter_json": c.filter_json,
        "article_count": len(c.items),
        "entry_ids": [item.miniflux_entry_id for item in c.items],
    }


@router.patch("/{collection_id}")
async def update_collection(
    collection_id: int, body: CollectionUpdate, db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    c = await db.get(Collection, collection_id)
    if not c:
        raise HTTPException(status_code=404, detail="Collection not found")
    if body.name is not None:
        c.name = body.name
    if body.description is not None:
        c.description = body.description
    if body.icon is not None:
        c.icon = body.icon
    if body.filter_json is not None:
        c.filter_json = body.filter_json
    if body.sort_order is not None:
        c.sort_order = body.sort_order
    await db.commit()
    return {"id": c.id, "name": c.name}


@router.delete("/{collection_id}")
async def delete_collection(
    collection_id: int, db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    c = await db.get(Collection, collection_id)
    if not c:
        raise HTTPException(status_code=404, detail="Collection not found")
    await db.delete(c)
    await db.commit()
    return {"status": "ok"}


@router.post("/{collection_id}/articles")
async def add_articles(
    collection_id: int, body: CollectionArticles, db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    c = await db.get(Collection, collection_id)
    if not c:
        raise HTTPException(status_code=404, detail="Collection not found")
    for entry_id in body.miniflux_entry_ids:
        existing = await db.execute(
            select(CollectionItem).where(
                CollectionItem.collection_id == collection_id,
                CollectionItem.miniflux_entry_id == entry_id,
            )
        )
        if not existing.scalars().first():
            db.add(CollectionItem(collection_id=collection_id, miniflux_entry_id=entry_id))
    await db.commit()
    return {"status": "ok"}


@router.delete("/{collection_id}/articles")
async def remove_articles(
    collection_id: int, body: CollectionArticles, db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    await db.execute(
        delete(CollectionItem).where(
            CollectionItem.collection_id == collection_id,
            CollectionItem.miniflux_entry_id.in_(body.miniflux_entry_ids),
        )
    )
    await db.commit()
    return {"status": "ok"}
