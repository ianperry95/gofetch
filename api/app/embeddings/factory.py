from app.config import settings
from app.embeddings.base import EmbeddingProvider


def create_embedding_provider() -> EmbeddingProvider:
    if settings.embedding_provider == "openai":
        from app.embeddings.openai_provider import OpenAIEmbeddingProvider

        return OpenAIEmbeddingProvider()
    else:
        from app.embeddings.onnx_provider import OnnxEmbeddingProvider

        return OnnxEmbeddingProvider()
