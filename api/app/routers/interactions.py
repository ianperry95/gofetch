import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.schemas import UserInteraction

logger = logging.getLogger(__name__)

router = APIRouter()


class InteractionCreate(BaseModel):
    miniflux_entry_id: int
    interaction_type: str  # "click", "read", "star", "hide"
    duration_seconds: int | None = None


@router.post("")
async def record_interaction(
    body: InteractionCreate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Record a user interaction with an article."""
    interaction = UserInteraction(
        miniflux_entry_id=body.miniflux_entry_id,
        interaction_type=body.interaction_type,
        duration_seconds=body.duration_seconds,
    )
    db.add(interaction)
    await db.commit()

    # Update user profile asynchronously for signal-bearing interactions
    if body.interaction_type in ("star", "read", "hide"):
        from app.services.user_profile_service import UserProfileService

        profile_service = UserProfileService()
        try:
            await profile_service.update_from_interaction(db, interaction)
        except Exception:
            logger.exception("Failed to update user profile from interaction")

    return {"status": "ok"}
