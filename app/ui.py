"""Streamlit chat UI.  Run:  streamlit run app/ui.py

By default it talks to the agent directly (one command, no server needed).
To use the FastAPI backend instead, set API_URL=http://localhost:8000 first.
"""
import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from src import storage
from src.agent import SupportAgent

API_URL = os.getenv("API_URL", "").rstrip("/")

st.set_page_config(page_title="Router Support Agent", page_icon="📡")


# ---------- backend (direct or via API) ----------
def send(message):
    if API_URL:
        import requests

        r = requests.post(f"{API_URL}/chat", json={"message": message, "session_id": st.session_state.sid}, timeout=60)
        r.raise_for_status()
        return r.json()
    return st.session_state.agent.chat(message)


def get_tickets():
    if API_URL:
        import requests

        return requests.get(f"{API_URL}/tickets", timeout=10).json()
    return storage.list_tickets()


def save_feedback(question, answer, rating):
    if API_URL:
        import requests

        requests.post(f"{API_URL}/feedback", json={"question": question, "answer": answer, "rating": rating}, timeout=10)
    else:
        storage.log_feedback(question, answer, rating)


# ---------- state ----------
def reset():
    st.session_state.messages = []
    st.session_state.sid = uuid.uuid4().hex
    st.session_state.logged = set()
    st.session_state.pop("agent", None)


if "messages" not in st.session_state:
    reset()
if not API_URL and "agent" not in st.session_state:
    try:
        st.session_state.agent = SupportAgent()
    except RuntimeError as e:
        st.error(str(e))
        st.stop()

# ---------- handle new input first, so sidebar and history show the update ----------
prompt = st.chat_input("Describe your router problem...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    try:
        with st.spinner("Searching the documentation..."):
            reply = send(prompt)
        st.session_state.messages.append({"role": "assistant", "content": reply["answer"], "meta": reply, "question": prompt})
    except Exception as e:
        st.session_state.messages.append({"role": "assistant", "content": f"Sorry, something went wrong: {e}"})

# ---------- sidebar ----------
with st.sidebar:
    st.header("📡 Router Support")
    st.caption("Answers come only from the documentation. Unsure? It offers a support ticket.")
    if st.button("New conversation"):
        reset()
        st.rerun()
    st.subheader("Support tickets")
    tickets = get_tickets()
    if not tickets:
        st.caption("No tickets yet.")
    for t in reversed(tickets[-10:]):
        with st.expander(f"{t['id']} · {t['summary'][:35]}"):
            st.write(t["summary"])
            st.caption(f"{t['time']} · {t['status']}")

# ---------- chat history ----------
st.title("Technical Support Agent")
if not st.session_state.messages:
    st.info("Try: *my wifi keeps cutting off*, *how do I reset my router*, or *what does a red internet light mean*.")

for i, m in enumerate(st.session_state.messages):
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        meta = m.get("meta")
        if not meta:
            continue
        if meta["action"] == "answer":
            st.caption(f"Confidence: {meta['confidence']:.0%}")
        for s in meta["sources"]:
            with st.expander(f"Source: {s['title']}"):
                st.write(s["snippet"])
                st.caption(f"{s['source']} · distance {s['distance']}")
        if meta["action"] in ("answer", "not_found"):
            rating = st.feedback("thumbs", key=f"fb_{i}")
            if rating is not None and i not in st.session_state.logged:
                st.session_state.logged.add(i)
                save_feedback(m["question"], m["content"], "up" if rating == 1 else "down")
                st.toast("Thanks for the feedback!")
