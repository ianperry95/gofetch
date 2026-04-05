"""Settings and OPML import/export endpoints."""

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.routers.schemas import ConfigUpdateRequest
from app.services.config_service import get_all_config, update_config
from app.services.miniflux_client import miniflux

router = APIRouter()


@router.get("/opml/export")
async def export_opml():
    """Export all feeds as OPML file."""
    opml = await miniflux.export_opml()
    return Response(
        content=opml,
        media_type="application/xml",
        headers={"Content-Disposition": "attachment; filename=gofetch-feeds.opml"},
    )


@router.post("/opml/import")
async def import_opml(file: UploadFile):
    """Import feeds from an OPML file."""
    content = await file.read()
    result = await miniflux.import_opml(content.decode("utf-8"))
    return {"status": "ok", "message": result.get("message", "Import complete")}


@router.get("/config")
async def get_config(db: AsyncSession = Depends(get_db)):
    """Get all configurable settings."""
    return await get_all_config(db)


@router.put("/config")
async def set_config(
    request: ConfigUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update configuration values."""
    result = await update_config(db, request.values)
    return result
