"""Step 1 of the pipeline: load documents -> chunk -> embed -> store in ChromaDB.

Run:  python src/ingest.py            (optional: --chunk-size 800 --overlap 100)
"""
import argparse
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import chromadb
from chromadb.config import Settings

from src import config
from src.embeddings import get_embedder

log = logging.getLogger(__name__)


def get_client(path=None):
    return chromadb.PersistentClient(
        path=str(path or config.DB_DIR), settings=Settings(anonymized_telemetry=False)
    )


def parse_doc(text, path):
    """Pull 'Source:' and 'Title:' lines off the top; the rest is the body."""
    source, title, body = str(path), os.path.basename(str(path)), []
    for line in text.splitlines():
        if line.startswith("Source:"):
            source = line.replace("Source:", "").strip()
        elif line.startswith("Title:"):
            title = line.replace("Title:", "").strip()
        else:
            body.append(line)
    return source, title, "\n".join(body).strip()


def read_pdf(path):
    from pypdf import PdfReader  # only needed if you add PDF manuals

    return "\n".join((page.extract_text() or "") for page in PdfReader(str(path)).pages)


def load_documents(data_dir=None):
    """Load every .md / .txt / .pdf file under data/raw."""
    data_dir = Path(data_dir or config.DATA_DIR)
    docs = []
    for path in sorted(data_dir.rglob("*")):
        if path.suffix.lower() not in {".md", ".txt", ".pdf"}:
            continue
        text = read_pdf(path) if path.suffix.lower() == ".pdf" else path.read_text(encoding="utf-8")
        source, title, body = parse_doc(text, path)
        if path.suffix.lower() == ".pdf":
            title = path.stem.replace("_", " ")
        if body:
            docs.append({"path": path.name, "source": source, "title": title, "body": body})
    return docs


def chunk_text(text, size=None, overlap=None):
    """Split text into chunks of about `size` characters, breaking on line ends
    so numbered steps are not cut in half. The last `overlap` characters are
    repeated at the start of the next chunk."""
    size = size or config.CHUNK_SIZE
    overlap = config.OVERLAP if overlap is None else overlap
    if len(text) <= size:
        return [text]
    chunks, current = [], ""
    for line in text.splitlines():
        if current and len(current) + len(line) + 1 > size:
            chunks.append(current.strip())
            current = current[-overlap:] if overlap else ""
        current += line + "\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks


def make_chunks(docs, size=None, overlap=None):
    """Return parallel lists (ids, texts, metadatas). The title is added to each
    chunk's text so the embedding knows the topic."""
    ids, texts, metas = [], [], []
    for doc in docs:
        for i, chunk in enumerate(chunk_text(doc["body"], size, overlap)):
            ids.append(f"{doc['path']}-{i}")
            texts.append(f"{doc['title']}\n{chunk}")
            metas.append({"source": doc["source"], "title": doc["title"], "chunk": i})
    return ids, texts, metas


def fill_collection(collection, ids, texts, metas, embedder, progress=False):
    vectors = embedder.encode(texts, progress=progress)
    for s in range(0, len(ids), 256):
        collection.add(
            ids=ids[s : s + 256],
            documents=texts[s : s + 256],
            embeddings=vectors[s : s + 256],
            metadatas=metas[s : s + 256],
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunk-size", type=int, default=config.CHUNK_SIZE)
    ap.add_argument("--overlap", type=int, default=config.OVERLAP)
    args = ap.parse_args()
    config.setup_logging()

    print("Loading embedding model...")
    embedder = get_embedder()
    docs = load_documents()
    print(f"Found {len(docs)} documents")
    if not docs:
        sys.exit("No documents found in data/raw. Run `python make_faqs.py` first.")

    client = get_client()
    try:  # start fresh so re-running never creates duplicates
        client.delete_collection(config.COLLECTION)
    except Exception:
        pass
    collection = client.create_collection(
        config.COLLECTION,
        metadata={"embedder": embedder.name, "chunk_size": args.chunk_size},
    )
    ids, texts, metas = make_chunks(docs, args.chunk_size, args.overlap)
    print(f"Created {len(texts)} chunks. Embedding...")
    fill_collection(collection, ids, texts, metas, embedder, progress=True)
    print(f"Stored {collection.count()} chunks in ChromaDB at {config.DB_DIR}")
    log.info("Ingested %d docs, %d chunks (embedder=%s)", len(docs), len(texts), embedder.name)


if __name__ == "__main__":
    main()
