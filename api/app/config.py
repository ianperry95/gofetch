from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://gofetch:changeme@localhost:5432/gofetch"

    # Miniflux
    miniflux_url: str = "http://localhost:8080"
    miniflux_api_key: str = ""
    miniflux_webhook_secret: str = ""

    # App
    secret_key: str = "change-this-to-a-random-string"

    # Embeddings
    embedding_provider: str = "onnx"  # "onnx" or "openai"
    embedding_model: str = "nomic-ai/nomic-embed-text-v1.5"
    embedding_dimension: int = 768

    # OpenAI
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"

    # Workers
    catchup_poll_interval_minutes: int = 5
    clustering_interval_minutes: int = 15
    ranking_interval_minutes: int = 5

    # Dedup
    dedup_similarity_threshold: float = 0.92
    dedup_lookback_days: int = 7

    # Clustering
    clustering_lookback_hours: int = 48
    clustering_min_cluster_size: int = 3
    clustering_distance_threshold: float = 0.35

    model_config = {"env_prefix": "GOFETCH_", "env_file": ".env", "extra": "ignore"}


settings = Settings()
