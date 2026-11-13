"""FastAPI backend.  Run:  uvicorn app.api:app --reload   (docs at /docs)"""
import sys
import uuid
from collections import OrderedDict
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src import config, storage
from src.agent import SupportAgent
from src.generate import llm_available
from src.retrieve import get_retriever

config.setup_logging()
app = FastAPI(title="Router Support RAG Agent", version="1.0")

MAX_SESSIONS = 500
_sessions = OrderedDict()  # session_id -> SupportAgent (each holds its own memory)


class ChatRequest(BaseModel):
    message: str = Field("", description="The user's message")
    session_id: Optional[str] = Field(None, description="Send the same id to keep conversation memory")


class Source(BaseModel):
    title: str
    source: str
    snippet: str
    distance: float


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
    confidence: float
    ticket_id: Optional[str]
    action: str
    session_id: str


class FeedbackRequest(BaseModel):
    question: str
    answer: str
    rating: str = Field(..., pattern="^(up|down)$")


def _agent_for(session_id):
    if session_id not in _sessions:
        _sessions[session_id] = SupportAgent()
        while len(_sessions) > MAX_SESSIONS:
            _sessions.popitem(last=False)
    return _sessions[session_id]


@app.get("/health")
def health():
    try:
        r = get_retriever()
        return {"status": "ok", "documents": r.count(), "embedder": r.embedder.name, "llm": llm_available()}
    except RuntimeError as e:
        return {"status": "degraded", "detail": str(e), "llm": llm_available()}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session_id = req.session_id or uuid.uuid4().hex
    try:
        reply = _agent_for(session_id).chat(req.message)
    except RuntimeError as e:  # e.g. database not built yet
        raise HTTPException(status_code=503, detail=str(e))
    return {**reply, "session_id": session_id}


@app.get("/tickets")
def tickets():
    return storage.list_tickets()


@app.post("/feedback")
def feedback(req: FeedbackRequest):
    storage.log_feedback(req.question, req.answer, req.rating)
    return {"status": "saved"}
