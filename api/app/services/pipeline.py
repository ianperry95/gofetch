"""Central pipeline that orchestrates embedding + dedup for new entries."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas import ArticleEmbedding
from app.services.dedup_service import DedupService
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(self, embedding_service: EmbeddingService) -> None:
        self.embedding_service = embedding_service
        self.dedup_service = DedupService()

    async def process_entries(self, db: AsyncSession, entries: list[dict]) -> None:
        """Run the full pipeline: embed → dedup for a batch of entries."""
        if not entries:
            return

        logger.info("Pipeline: processing %d entries", len(entries))

        # Step 1: Compute and store embeddings
        new_embeddings = await self.embedding_service.embed_entries(db, entries)

        if not new_embeddings:
            return

        # Step 2: Check each new embedding for duplicates
        for emb in new_embeddings:
            try:
                await self.dedup_service.process_duplicates(db, emb)
            except Exception:
                logger.exception(
                    "Dedup failed for entry %d", emb.miniflux_entry_id
                )

        logger.info("Pipeline: done processing %d new entries", len(new_embeddings))
