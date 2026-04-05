import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.schemas import (
    ArticleEmbedding,
    ArticleScore,
    DuplicateGroup,
    DuplicateMember,
)

logger = logging.getLogger(__name__)


class DedupService:
    async def find_duplicates(
        self, db: AsyncSession, embedding_row: ArticleEmbedding
    ) -> list[tuple[int, float]]:
        """Find entries similar to the given embedding within the lookback window.

        Returns list of (miniflux_entry_id, similarity_score) tuples.
        """
        lookback = datetime.now(timezone.utc) - timedelta(days=settings.dedup_lookback_days)

        # Use pgvector cosine distance operator: 1 - (a <=> b) = cosine similarity
        query = text("""
            SELECT miniflux_entry_id, 1 - (embedding <=> :vec) AS similarity
            FROM article_embeddings
            WHERE miniflux_entry_id != :entry_id
              AND published_at > :lookback
            ORDER BY embedding <=> :vec
            LIMIT 10
        """)

        result = await db.execute(
            query,
            {
                "vec": str(embedding_row.embedding),
                "entry_id": embedding_row.miniflux_entry_id,
                "lookback": lookback,
            },
        )

        return [
            (row[0], float(row[1]))
            for row in result.all()
            if float(row[1]) >= settings.dedup_similarity_threshold
        ]

    async def process_duplicates(
        self, db: AsyncSession, embedding_row: ArticleEmbedding
    ) -> DuplicateGroup | None:
        """Check an embedding for duplicates and create/update groups as needed."""
        similar = await self.find_duplicates(db, embedding_row)

        if not similar:
            return None

        logger.info(
            "Entry %d has %d duplicates (threshold=%.2f)",
            embedding_row.miniflux_entry_id,
            len(similar),
            settings.dedup_similarity_threshold,
        )

        # Check if any of the similar entries are already in a group
        similar_ids = [s[0] for s in similar]
        existing_member = await db.execute(
            select(DuplicateMember).where(
                DuplicateMember.miniflux_entry_id.in_(similar_ids)
            )
        )
        existing = existing_member.scalars().first()

        if existing:
            # Add to existing group
            group = await db.get(DuplicateGroup, existing.group_id)
        else:
            # Create new group — pick the earliest entry as canonical
            # (could also pick by content length or source quality)
            canonical_id = await self._pick_canonical(
                db, [embedding_row.miniflux_entry_id] + similar_ids
            )
            group = DuplicateGroup(canonical_entry_id=canonical_id)
            db.add(group)
            await db.flush()

            # Add the similar entries that triggered this group
            for entry_id, score in similar:
                member = DuplicateMember(
                    group_id=group.id,
                    miniflux_entry_id=entry_id,
                    similarity_score=score,
                )
                db.add(member)

        # Check if current entry is already a member
        already_member = await db.execute(
            select(DuplicateMember).where(
                DuplicateMember.miniflux_entry_id == embedding_row.miniflux_entry_id,
                DuplicateMember.group_id == group.id,
            )
        )
        if not already_member.scalars().first():
            # Add current entry to group
            best_similarity = max(s[1] for s in similar)
            member = DuplicateMember(
                group_id=group.id,
                miniflux_entry_id=embedding_row.miniflux_entry_id,
                similarity_score=best_similarity,
            )
            db.add(member)

        # Mark non-canonical entries as duplicates in article_scores
        await self._update_scores(db, group)

        await db.commit()
        return group

    async def _pick_canonical(self, db: AsyncSession, entry_ids: list[int]) -> int:
        """Pick the canonical entry from a set of duplicates.

        Prefers the entry with the longest content (proxy for most complete article).
        Falls back to the earliest published.
        """
        result = await db.execute(
            select(ArticleEmbedding)
            .where(ArticleEmbedding.miniflux_entry_id.in_(entry_ids))
            .order_by(ArticleEmbedding.published_at.asc())
        )
        rows = result.scalars().all()
        if not rows:
            return entry_ids[0]
        # For now, just pick the earliest published
        return rows[0].miniflux_entry_id

    async def _update_scores(self, db: AsyncSession, group: DuplicateGroup) -> None:
        """Mark all non-canonical members as duplicates in article_scores."""
        result = await db.execute(
            select(DuplicateMember).where(DuplicateMember.group_id == group.id)
        )
        members = result.scalars().all()

        for member in members:
            entry_id = member.miniflux_entry_id
            is_dup = entry_id != group.canonical_entry_id

            # Upsert article_score
            existing = await db.get(ArticleScore, entry_id)
            if existing:
                existing.is_duplicate = is_dup
                existing.canonical_entry_id = group.canonical_entry_id if is_dup else None
            else:
                score = ArticleScore(
                    miniflux_entry_id=entry_id,
                    is_duplicate=is_dup,
                    canonical_entry_id=group.canonical_entry_id if is_dup else None,
                )
                db.add(score)
