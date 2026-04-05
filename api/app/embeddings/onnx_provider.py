import logging
from pathlib import Path

import numpy as np
import onnxruntime as ort
from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer

from app.config import settings
from app.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)

ONNX_FILENAME = "onnx/model.onnx"
TOKENIZER_FILENAME = "tokenizer.json"


class OnnxEmbeddingProvider(EmbeddingProvider):
    """Local embedding provider using ONNX Runtime directly (no PyTorch)."""

    def __init__(self) -> None:
        self._model_name = settings.embedding_model
        self._dimension = settings.embedding_dimension
        self._session: ort.InferenceSession | None = None
        self._tokenizer: Tokenizer | None = None

    def _load_model(self):
        if self._session is not None:
            return
        logger.info("Loading embedding model: %s", self._model_name)

        model_path = hf_hub_download(self._model_name, filename=ONNX_FILENAME)
        tokenizer_path = hf_hub_download(self._model_name, filename=TOKENIZER_FILENAME)

        opts = ort.SessionOptions()
        opts.inter_op_num_threads = 1
        opts.intra_op_num_threads = 4
        self._session = ort.InferenceSession(model_path, sess_options=opts)
        self._tokenizer = Tokenizer.from_file(tokenizer_path)

        logger.info("Model loaded successfully (dim=%d)", self._dimension)

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def model_name(self) -> str:
        return self._model_name

    def _encode_batch(self, texts: list[str]) -> np.ndarray:
        assert self._tokenizer is not None
        assert self._session is not None

        self._tokenizer.enable_padding()
        self._tokenizer.enable_truncation(max_length=512)
        encoded = self._tokenizer.encode_batch(texts)

        input_ids = np.array([e.ids for e in encoded], dtype=np.int64)
        attention_mask = np.array([e.attention_mask for e in encoded], dtype=np.int64)
        token_type_ids = np.zeros_like(input_ids)

        feeds = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "token_type_ids": token_type_ids,
        }

        # Only pass inputs the model actually expects
        expected = {inp.name for inp in self._session.get_inputs()}
        feeds = {k: v for k, v in feeds.items() if k in expected}

        outputs = self._session.run(None, feeds)
        # Mean pooling over token embeddings, masked by attention
        token_embeddings = outputs[0]  # (batch, seq_len, hidden)
        mask = attention_mask[:, :, np.newaxis].astype(np.float32)
        pooled = (token_embeddings * mask).sum(axis=1) / mask.sum(axis=1).clip(min=1e-9)
        return pooled

    async def embed(self, texts: list[str]) -> list[list[float]]:
        self._load_model()

        # nomic-embed-text-v1.5 requires a task prefix for best results
        prefixed = [f"search_document: {t}" for t in texts]

        # Process in batches
        all_embeddings = []
        for i in range(0, len(prefixed), 32):
            batch = prefixed[i : i + 32]
            all_embeddings.append(self._encode_batch(batch))

        embeddings = np.concatenate(all_embeddings, axis=0)

        # Matryoshka dimensionality reduction
        if embeddings.shape[1] > self._dimension:
            embeddings = embeddings[:, : self._dimension]

        # L2 normalize
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / norms.clip(min=1e-9)

        return embeddings.tolist()
