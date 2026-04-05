import logging
import math
from datetime import datetime, timezone

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas import ArticleEmbedding, ArticleScore
from app.services.user_profile_service import UserProfileService

logger = logging.getLogger(__name__)

# Ranking weights
W_RELEVANCE = 0.5
W_RECENCY = 0.3
W_SOURCE = 0.2

# Time decay half-life in hours
RECENCY_HALF_LIFE = 24.0


class RankingService:
    def __init__(self) -> None:
        self.profile_service = UserProfileService()

    async def rank_entries(self, db: AsyncSession, limit: int = 500) -> int:
        """Recompute scores for recent unscored or stale entries. Returns count updated."""
        interest_vec = await self.profile_service.get_interest_vector(db)

        # Fetch embeddings that need scoring (no score or stale)
        result = await db.execute(
            select(ArticleEmbedding)
            .outerjoin(
                ArticleScore,
                ArticleEmbedding.miniflux_entry_id == ArticleScore.miniflux_entry_id,
            )
            .where(
                (ArticleScore.miniflux_entry_id.is_(None))
                | (ArticleScore.final_score.is_(None))
            )
            .order_by(ArticleEmbedding.created_at.desc())
            .limit(limit)
        )
        embeddings = result.scalars().all()

        if not embeddings:
            return 0

        now = datetime.now(timezone.utc)
        updated = 0

        for emb in embeddings:
            relevance = self._compute_relevance(emb, interest_vec)
            recency = self._compute_recency(emb, now)
            source = 0.5  # Placeholder — feed quality scoring comes later

            final = W_RELEVANCE * relevance + W_RECENCY * recency + W_SOURCE * source

            # Upsert
            existing = await db.get(ArticleScore, emb.miniflux_entry_id)
            if existing:
                existing.relevance_score = relevance
                existing.recency_score = recency
                existing.source_score = source
                existing.final_score = final
            else:
                score = ArticleScore(
                    miniflux_entry_id=emb.miniflux_entry_id,
                    relevance_score=relevance,
                    recency_score=recency,
                    source_score=source,
                    final_score=final,
                )
                db.add(score)
            updated += 1

        await db.commit()
        logger.info("Ranked %d entries", updated)
        return updated

    def _compute_relevance(
        self, emb: ArticleEmbedding, interest_vec: np.ndarray | None
    ) -> float:
        """Cosine similarity between article embedding and user interest vector."""
        if interest_vec is None:
            return 0.5  # Neutral score when no profile exists yet

        article_vec = np.array(emb.embedding, dtype=np.float64)
        dot = np.dot(article_vec, interest_vec)
        norm_a = np.linalg.norm(article_vec)
        norm_b = np.linalg.norm(interest_vec)
        if norm_a < 1e-10 or norm_b < 1e-10:
            return 0.5
        similarity = dot / (norm_a * norm_b)
        # Map from [-1, 1] to [0, 1]
        return float((similarity + 1) / 2)

    def _compute_recency(self, emb: ArticleEmbedding, now: datetime) -> float:
        """Exponential time decay score."""
        if emb.published_at is None:
            return 0.5
        published = emb.published_at
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
        hours_ago = (now - published).total_seconds() / 3600
        return float(math.exp(-math.log(2) * hours_ago / RECENCY_HALF_LIFE))
