"""Central settings. Every other file imports its settings from here."""
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

# ---- paths ----
DATA_DIR = ROOT / "data" / "raw"
DB_DIR = ROOT / "chroma_db"
STORAGE_DIR = ROOT / "storage"
TICKETS_FILE = STORAGE_DIR / "tickets.json"
FEEDBACK_FILE = STORAGE_DIR / "feedback.jsonl"
LOG_DIR = ROOT / "logs"
COLLECTION = "support_docs"

# ---- retrieval ----
EMBEDDER = os.getenv("EMBEDDER", "minilm")  # "minilm" (default) or "hash" (offline fallback)
EMBED_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "600"))
OVERLAP = int(os.getenv("OVERLAP", "100"))
TOP_K = int(os.getenv("TOP_K", "4"))
# Lower distance = better match. If the best chunk is farther than this, we do NOT
# call the LLM; we say "not found" and offer a ticket. None = use the embedder's default.
_thr = os.getenv("DISTANCE_THRESHOLD")
DISTANCE_THRESHOLD = float(_thr) if _thr else None

# ---- LLM (Groq, free tier) ----
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
# Some free Groq models reject max_tokens above 512, so we cap it at 500.
MAX_TOKENS = min(int(os.getenv("MAX_TOKENS", "500")), 500)

# ---- conversation ----
MAX_HISTORY_TURNS = 6  # remember the last 6 user+assistant exchanges
MAX_MESSAGE_CHARS = 1000


def setup_logging():
    """Log to logs/app.log (INFO) and to the console (WARNING+)."""
    LOG_DIR.mkdir(exist_ok=True)
    root = logging.getLogger()
    if root.handlers:
        return
    root.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    fh = logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8")
    fh.setFormatter(fmt)
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(fmt)
    root.addHandler(fh)
    root.addHandler(ch)
    for noisy in ("httpx", "httpcore", "chromadb", "urllib3", "sentence_transformers"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
