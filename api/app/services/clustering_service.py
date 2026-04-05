import logging
from collections import Counter
from datetime import datetime, timedelta, timezone

import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.schemas import ArticleEmbedding, ArticleScore, ClusterMember, TopicCluster

logger = logging.getLogger(__name__)


class ClusteringService:
    async def run_clustering(self, db: AsyncSession) -> int:
        """Cluster recent articles by embedding similarity. Returns number of clusters created."""
        lookback = datetime.now(timezone.utc) - timedelta(hours=settings.clustering_lookback_hours)

        result = await db.execute(
            select(ArticleEmbedding)
            .where(ArticleEmbedding.published_at > lookback)
            .order_by(ArticleEmbedding.published_at.desc())
        )
        embeddings = result.scalars().all()

        if len(embeddings) < settings.clustering_min_cluster_size:
            logger.debug("Not enough articles (%d) for clustering", len(embeddings))
            return 0

        # Build matrix
        ids = [e.miniflux_entry_id for e in embeddings]
        titles = [e.title or "" for e in embeddings]
        matrix = np.array([e.embedding for e in embeddings], dtype=np.float64)

        # Run agglomerative clustering with cosine distance
        clustering = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=settings.clustering_distance_threshold,
            metric="cosine",
            linkage="average",
        )
        labels = clustering.fit_predict(matrix)

        # Group by label
        clusters: dict[int, list[int]] = {}
        for idx, label in enumerate(labels):
            if label == -1:
                continue
            clusters.setdefault(label, []).append(idx)

        # Filter: only keep clusters with enough members
        valid_clusters = {
            k: v
            for k, v in clusters.items()
            if len(v) >= settings.clustering_min_cluster_size
        }

        if not valid_clusters:
            return 0

        # Clear old clusters in the lookback window
        await db.execute(delete(TopicCluster).where(TopicCluster.expires_at.isnot(None)))
        await db.flush()

        # Create new clusters
        created = 0
        for label, member_indices in valid_clusters.items():
            member_vecs = matrix[member_indices]
            centroid = member_vecs.mean(axis=0)
            norm = np.linalg.norm(centroid)
            if norm > 1e-10:
                centroid = centroid / norm

            member_titles = [titles[i] for i in member_indices]
            cluster_label = self._generate_label(member_titles)

            cluster = TopicCluster(
                label=cluster_label,
                article_count=len(member_indices),
                centroid=centroid.tolist(),
                expires_at=datetime.now(timezone.utc) + timedelta(hours=settings.clustering_lookback_hours),
            )
            db.add(cluster)
            await db.flush()

            for idx in member_indices:
                entry_id = ids[idx]
                distance = float(np.linalg.norm(matrix[idx] - centroid))
                member = ClusterMember(
                    cluster_id=cluster.id,
                    miniflux_entry_id=entry_id,
                    distance=distance,
                )
                db.add(member)

                # Update article_scores with cluster_id
                existing_score = await db.get(ArticleScore, entry_id)
                if existing_score:
                    existing_score.cluster_id = cluster.id
                else:
                    score = ArticleScore(
                        miniflux_entry_id=entry_id,
                        cluster_id=cluster.id,
                    )
                    db.add(score)

            created += 1

        await db.commit()
        logger.info("Created %d topic clusters from %d articles", created, len(embeddings))
        return created

    def _generate_label(self, titles: list[str]) -> str:
        """Generate a cluster label from member titles using most common words."""
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "can", "shall", "to", "of", "in", "for",
            "on", "with", "at", "by", "from", "as", "into", "through", "during",
            "before", "after", "above", "below", "between", "out", "off", "over",
            "under", "again", "further", "then", "once", "and", "but", "or", "nor",
            "not", "so", "yet", "both", "either", "neither", "each", "every", "all",
            "any", "few", "more", "most", "other", "some", "such", "no", "only",
            "own", "same", "than", "too", "very", "just", "about", "up", "its",
            "it", "this", "that", "these", "those", "he", "she", "they", "we",
            "you", "i", "me", "him", "her", "us", "them", "my", "your", "his",
            "our", "their", "what", "which", "who", "whom", "how", "when", "where",
            "why", "new", "says", "said", "also", "like", "get", "gets", "got",
        }
        words: list[str] = []
        for title in titles:
            for word in title.lower().split():
                cleaned = word.strip(".,!?:;\"'()[]{}—-–")
                if cleaned and cleaned not in stop_words and len(cleaned) > 2:
                    words.append(cleaned)

        if not words:
            return "Untitled Topic"

        counter = Counter(words)
        top = [w for w, _ in counter.most_common(4)]
        return " ".join(w.capitalize() for w in top)
