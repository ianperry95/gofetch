from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.schemas import SavedView

router = APIRouter()


class SavedViewCreate(BaseModel):
    name: str
    filter_json: dict
    sort_by: str = "ranked"
    layout: str = "cards"
    pinned: bool = False


class SavedViewUpdate(BaseModel):
    name: str | None = None
    filter_json: dict | None = None
    sort_by: str | None = None
    layout: str | None = None
    pinned: bool | None = None


@router.get("")
async def list_saved_views(db: AsyncSession = Depends(get_db)) -> list[dict[str, Any]]:
    result = await db.execute(
        select(SavedView).order_by(SavedView.pinned.desc(), SavedView.name)
    )
    return [
        {
            "id": v.id,
            "name": v.name,
            "filter_json": v.filter_json,
            "sort_by": v.sort_by,
            "layout": v.layout,
            "pinned": v.pinned,
        }
        for v in result.scalars().all()
    ]


@router.post("")
async def create_saved_view(
    body: SavedViewCreate, db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    view = SavedView(
        name=body.name,
        filter_json=body.filter_json,
        sort_by=body.sort_by,
        layout=body.layout,
        pinned=body.pinned,
    )
    db.add(view)
    await db.commit()
    await db.refresh(view)
    return {"id": view.id, "name": view.name}


@router.get("/{view_id}")
async def get_saved_view(
    view_id: int, db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    v = await db.get(SavedView, view_id)
    if not v:
        raise HTTPException(status_code=404, detail="Saved view not found")
    return {
        "id": v.id,
        "name": v.name,
        "filter_json": v.filter_json,
        "sort_by": v.sort_by,
        "layout": v.layout,
        "pinned": v.pinned,
    }


@router.patch("/{view_id}")
async def update_saved_view(
    view_id: int, body: SavedViewUpdate, db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    v = await db.get(SavedView, view_id)
    if not v:
        raise HTTPException(status_code=404, detail="Saved view not found")
    if body.name is not None:
        v.name = body.name
    if body.filter_json is not None:
        v.filter_json = body.filter_json
    if body.sort_by is not None:
        v.sort_by = body.sort_by
    if body.layout is not None:
        v.layout = body.layout
    if body.pinned is not None:
        v.pinned = body.pinned
    await db.commit()
    return {"id": v.id, "name": v.name}


@router.delete("/{view_id}")
async def delete_saved_view(
    view_id: int, db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    v = await db.get(SavedView, view_id)
    if not v:
        raise HTTPException(status_code=404, detail="Saved view not found")
    await db.delete(v)
    await db.commit()
    return {"status": "ok"}
