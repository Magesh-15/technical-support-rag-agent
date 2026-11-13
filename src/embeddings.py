"""Embedders turn text into vectors. Default: MiniLM (semantic, local, free).
Fallback: a simple hashing embedder that needs no download (used for offline tests)."""
import math
import zlib
from collections import Counter

from src import config
from src.text_utils import tokenize

# Words that appear in almost every document carry little meaning (hashing embedder only).
_COMMON = {"router": 0.4, "wifi": 0.5, "network": 0.5, "internet": 0.6}


class HashingEmbedder:
    name = "hash"
    dim = 384
    recommended_threshold = 1.5

    def encode(self, texts, progress=False):
        return [self._one(t) for t in texts]

    def _one(self, text):
        toks = tokenize(text)
        feats = Counter(toks)
        bigrams = Counter(f"{a}_{b}" for a, b in zip(toks, toks[1:]))
        vec = [0.0] * self.dim
        for f, c in feats.items():
            vec[zlib.crc32(f.encode()) % self.dim] += (1 + math.log(c)) * _COMMON.get(f, 1.0)
        for f, c in bigrams.items():
            vec[zlib.crc32(f.encode()) % self.dim] += 0.5 * (1 + math.log(c))
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]


class MiniLMEmbedder:
    name = "minilm"
    recommended_threshold = 1.3

    def __init__(self):
        from sentence_transformers import SentenceTransformer  # heavy import, so lazy

        self.model = SentenceTransformer(config.EMBED_MODEL)

    def encode(self, texts, progress=False):
        return self.model.encode(list(texts), show_progress_bar=progress).tolist()


_cache = {}


def get_embedder(name=None):
    name = name or config.EMBEDDER
    if name not in _cache:
        _cache[name] = HashingEmbedder() if name == "hash" else MiniLMEmbedder()
    return _cache[name]
