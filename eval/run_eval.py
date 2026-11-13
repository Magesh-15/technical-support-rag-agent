"""Measure retrieval quality.

  python eval/run_eval.py             -> evaluate the current database (k = TOP_K)
  python eval/run_eval.py --compare   -> compare chunk size 500 vs 800 and k = 3 vs 5

Metrics (on answerable questions): hit rate@k = is the right document in the top k?
MRR = how high is it ranked? On unanswerable questions: refusal accuracy = did the
best distance exceed the threshold, so the bot would refuse instead of guessing?
"""
import argparse
import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import chromadb
from chromadb.config import Settings

from src import config
from src.embeddings import get_embedder
from src.ingest import fill_collection, load_documents, make_chunks
from src.retrieve import Retriever


def evaluate(retriever, items, k):
    hits = mrr = answerable = refuse_ok = unanswerable = 0
    misses = []
    for it in items:
        res = retriever.retrieve(it["question"], k=k)
        best = res[0]["distance"] if res else 99.0
        if it["expected_title"]:
            answerable += 1
            titles = list(dict.fromkeys(r["title"] for r in res))
            if it["expected_title"] in titles:
                hits += 1
                mrr += 1 / (titles.index(it["expected_title"]) + 1)
            else:
                misses.append((it["question"], it["expected_title"], titles[:2]))
        else:
            unanswerable += 1
            if best > retriever.threshold:
                refuse_ok += 1
            else:
                misses.append((it["question"], "(should refuse)", [f"best distance {best:.2f}"]))
    return {
        "hit_rate": hits / max(answerable, 1),
        "mrr": mrr / max(answerable, 1),
        "refusal_acc": refuse_ok / max(unanswerable, 1),
        "misses": misses,
    }


def table(rows):
    out = ["| Chunk size | k | Hit rate@k | MRR | Refusal accuracy |", "|---|---|---|---|---|"]
    for size, k, r in rows:
        out.append(f"| {size} | {k} | {r['hit_rate']:.0%} | {r['mrr']:.2f} | {r['refusal_acc']:.0%} |")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--compare", action="store_true")
    args = ap.parse_args()
    items = json.loads((ROOT / "eval" / "test_set.json").read_text(encoding="utf-8"))
    embedder = get_embedder()
    rows = []

    if args.compare:
        docs = load_documents()
        client = chromadb.EphemeralClient(settings=Settings(anonymized_telemetry=False))
        for size in (500, 800):
            col = client.create_collection(f"eval_{size}_{uuid.uuid4().hex[:6]}")
            fill_collection(col, *make_chunks(docs, size, config.OVERLAP), embedder)
            retriever = Retriever(embedder, collection=col)
            for k in (3, 5):
                rows.append((size, k, evaluate(retriever, items, k)))
    else:
        retriever = Retriever(embedder)
        meta = retriever.collection.metadata or {}
        rows.append((meta.get("chunk_size", config.CHUNK_SIZE), config.TOP_K, evaluate(retriever, items, config.TOP_K)))

    md = f"Embedder: `{embedder.name}`, {len(items)} test questions\n\n" + table(rows)
    print("\n" + md)
    worst = rows[0][2]["misses"]
    if worst:
        print("\nMissed cases (first config):")
        for q, exp, got in worst:
            print(f"  - {q!r}: expected {exp}, got {got}")
    (ROOT / "eval" / "results.md").write_text(md + "\n", encoding="utf-8")
    print("\nSaved eval/results.md")


if __name__ == "__main__":
    main()
