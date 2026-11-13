"""Step 2: search the vector database."""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config
from src.embeddings import get_embedder
from src.ingest import get_client

log = logging.getLogger(__name__)


class Retriever:
    def __init__(self, embedder=None, collection=None):
        self.embedder = embedder or get_embedder()
        if collection is None:
            try:
                collection = get_client().get_collection(config.COLLECTION)
            except Exception as e:
                raise RuntimeError(
                    "Vector database not found. Run `python src/ingest.py` first."
                ) from e
            built_with = (collection.metadata or {}).get("embedder")
            if built_with and built_with != self.embedder.name:
                log.warning(
                    "DB was built with embedder '%s' but you are using '%s'. "
                    "Re-run `python src/ingest.py`.", built_with, self.embedder.name,
                )
        self.collection = collection

    @property
    def threshold(self):
        if config.DISTANCE_THRESHOLD is not None:
            return config.DISTANCE_THRESHOLD
        return self.embedder.recommended_threshold

    def count(self):
        return self.collection.count()

    def retrieve(self, query, k=None):
        """Return the top-k chunks (best first) as a list of dicts."""
        k = k or config.TOP_K
        vec = self.embedder.encode([query])
        res = self.collection.query(query_embeddings=vec, n_results=k)
        out = []
        for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
            out.append({
                "text": doc,
                "source": meta["source"],
                "title": meta["title"],
                "chunk": meta.get("chunk", 0),
                "distance": float(dist),
            })
        return out


_shared = None


def get_retriever():
    """One shared Retriever per process (loading the model is slow)."""
    global _shared
    if _shared is None:
        _shared = Retriever()
    return _shared


def retrieve(query, k=None):
    return get_retriever().retrieve(query, k)
