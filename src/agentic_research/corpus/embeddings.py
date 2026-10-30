"""Embedding implementations (Notion D2)."""

import hashlib
import re
from collections.abc import Sequence

import numpy as np
from pydantic import SecretStr

from ..contracts import ProviderError

_TOKEN = re.compile(r"[0-9a-z가-힣]+")


class HashEmbedding:
    """Deterministic, offline embedding from hashed word and character n-grams.

    Works for mixed Korean/English text without downloads or keys, so tests and
    CI are reproducible. Retrieval quality is lexical, not semantic.
    """

    def __init__(self, dim: int = 512) -> None:
        self.dim = dim
        self.name = f"hash{dim}"

    def _features(self, text: str) -> list[str]:
        tokens = _TOKEN.findall(text.lower())
        features = [f"w:{token}" for token in tokens]
        for token in tokens:
            padded = f"#{token}#"
            features += [f"c:{padded[i:i + 3]}" for i in range(len(padded) - 2)]
        return features

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        vectors = np.zeros((len(texts), self.dim), dtype=np.float32)
        for row, text in enumerate(texts):
            for feature in self._features(text):
                digest = hashlib.blake2b(feature.encode(), digest_size=8).digest()
                value = int.from_bytes(digest, "little")
                sign = 1.0 if value >> 63 else -1.0
                vectors[row, value % self.dim] += sign
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return (vectors / norms).tolist()


class OpenAIEmbedding:
    def __init__(self, model: str, api_key: SecretStr) -> None:
        from langchain_openai import OpenAIEmbeddings

        self.name = f"openai-{model}"
        self._client = OpenAIEmbeddings(model=model, api_key=api_key)

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        try:
            return self._client.embed_documents(list(texts))
        except Exception as error:  # provider or network failure
            raise ProviderError(f"{self.name}: {error}") from error
