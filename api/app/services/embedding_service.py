import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.embeddings.base import EmbeddingProvider
from app.models.schemas import ArticleEmbedding
from app.utils.html import strip_html

logger = logging.getLogger(__name__)

MAX_CONTENT_CHARS = 4000  # ~1000 tokens, well within nomic's 8K context


class EmbeddingService:
    def __init__(self, provider: EmbeddingProvider) -> None:
        self.provider = provider

    def prepare_text(self, entry: dict) -> str:
        """Prepare article text for embedding: title + stripped content."""
        title = entry.get("title", "")
        content = strip_html(entry.get("content", ""))
        if content:
            content = content[:MAX_CONTENT_CHARS]
        return f"{title}. {content}" if content else title

    async def get_existing_ids(self, db: AsyncSession, entry_ids: list[int]) -> set[int]:
        """Return the set of miniflux_entry_ids that already have embeddings."""
        if not entry_ids:
            return set()
        result = await db.execute(
            select(ArticleEmbedding.miniflux_entry_id).where(
                ArticleEmbedding.miniflux_entry_id.in_(entry_ids)
            )
        )
        return {row[0] for row in result.all()}

    async def embed_entries(
        self, db: AsyncSession, entries: list[dict]
    ) -> list[ArticleEmbedding]:
        """Compute embeddings for entries and store them. Returns the new ArticleEmbedding rows."""
        if not entries:
            return []

        # Filter out entries we've already embedded
        entry_ids = [e["id"] for e in entries]
        existing = await self.get_existing_ids(db, entry_ids)
        new_entries = [e for e in entries if e["id"] not in existing]

        if not new_entries:
            logger.debug("All %d entries already embedded, skipping", len(entries))
            return []

        logger.info("Embedding %d new entries (skipped %d existing)", len(new_entries), len(existing))

        # Prepare texts and compute embeddings
        texts = [self.prepare_text(e) for e in new_entries]
        vectors = await self.provider.embed(texts)

        # Store embeddings
        rows = []
        for entry, vector in zip(new_entries, vectors):
            published_at = entry.get("published_at")
            if isinstance(published_at, str):
                try:
                    published_at = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    published_at = None

            row = ArticleEmbedding(
                miniflux_entry_id=entry["id"],
                miniflux_feed_id=entry.get("feed_id", 0),
                embedding=vector,
                model_name=self.provider.model_name,
                title=entry.get("title"),
                url=entry.get("url"),
                published_at=published_at,
            )
            db.add(row)
            rows.append(row)

        await db.commit()
        logger.info("Stored %d embeddings", len(rows))
        return rows
