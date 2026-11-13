"""Tiny file-based storage for support tickets and user feedback."""
import json
import threading
from datetime import datetime, timezone

from src import config

_lock = threading.Lock()


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def list_tickets(path=None):
    path = path or config.TICKETS_FILE
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def create_ticket(summary, details, path=None):
    """Save a ticket to tickets.json and return it."""
    path = path or config.TICKETS_FILE
    with _lock:
        tickets = list_tickets(path)
        ticket = {
            "id": f"T-{len(tickets) + 1:04d}",
            "time": _now(),
            "summary": summary[:200],
            "details": details,
            "status": "open",
        }
        tickets.append(ticket)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(tickets, indent=2, ensure_ascii=False), encoding="utf-8")
    return ticket


def log_feedback(question, answer, rating, path=None):
    """Append one thumbs up/down record (rating: 'up' or 'down')."""
    path = path or config.FEEDBACK_FILE
    record = {"time": _now(), "rating": rating, "question": question, "answer": answer}
    with _lock:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
