import logging

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.schemas import ArticleEmbedding, UserInteraction, UserProfile

logger = logging.getLogger(__name__)

# Exponential moving average decay — how much the new signal shifts the vector
POSITIVE_DECAY = 0.05
NEGATIVE_DECAY = 0.05
# Minimum read duration (seconds) to count as a positive signal
MIN_READ_DURATION = 60


class UserProfileService:
    async def get_or_create_profile(self, db: AsyncSession) -> UserProfile:
        result = await db.execute(select(UserProfile).limit(1))
        profile = result.scalars().first()
        if profile is None:
            dim = settings.embedding_dimension
            profile = UserProfile(
                interest_vector=np.zeros(dim).tolist(),
                disinterest_vector=np.zeros(dim).tolist(),
            )
            db.add(profile)
            await db.flush()
        return profile

    async def update_from_interaction(
        self, db: AsyncSession, interaction: UserInteraction
    ) -> None:
        """Shift the user profile vectors based on the interaction."""
        # Get the article embedding
        result = await db.execute(
            select(ArticleEmbedding).where(
                ArticleEmbedding.miniflux_entry_id == interaction.miniflux_entry_id
            )
        )
        emb_row = result.scalars().first()
        if emb_row is None or emb_row.embedding is None:
            return

        article_vec = np.array(emb_row.embedding, dtype=np.float64)
        profile = await self.get_or_create_profile(db)

        if interaction.interaction_type == "hide":
            # Negative signal
            current = np.array(profile.disinterest_vector, dtype=np.float64)
            updated = self._ema_update(current, article_vec, NEGATIVE_DECAY)
            profile.disinterest_vector = updated.tolist()
        elif interaction.interaction_type == "star":
            # Strong positive signal
            current = np.array(profile.interest_vector, dtype=np.float64)
            updated = self._ema_update(current, article_vec, POSITIVE_DECAY)
            profile.interest_vector = updated.tolist()
        elif interaction.interaction_type == "read":
            # Positive signal only if read long enough
            if (interaction.duration_seconds or 0) >= MIN_READ_DURATION:
                current = np.array(profile.interest_vector, dtype=np.float64)
                updated = self._ema_update(current, article_vec, POSITIVE_DECAY)
                profile.interest_vector = updated.tolist()

        await db.commit()

    def _ema_update(
        self, current: np.ndarray, new: np.ndarray, decay: float
    ) -> np.ndarray:
        """Exponential moving average update with renormalization."""
        # If current is zero (fresh profile), just use the new vector
        if np.linalg.norm(current) < 1e-10:
            return new / (np.linalg.norm(new) + 1e-10)

        updated = (1 - decay) * current + decay * new
        norm = np.linalg.norm(updated)
        if norm > 1e-10:
            updated = updated / norm
        return updated

    async def get_interest_vector(self, db: AsyncSession) -> np.ndarray | None:
        """Return the interest vector, or None if no profile exists."""
        profile = await self.get_or_create_profile(db)
        vec = np.array(profile.interest_vector, dtype=np.float64)
        if np.linalg.norm(vec) < 1e-10:
            return None
        return vec

    async def get_disinterest_vector(self, db: AsyncSession) -> np.ndarray | None:
        """Return the disinterest vector, or None if no profile exists."""
        profile = await self.get_or_create_profile(db)
        vec = np.array(profile.disinterest_vector, dtype=np.float64)
        if np.linalg.norm(vec) < 1e-10:
            return None
        return vec
