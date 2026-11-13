"""Command-line chat.  Run:  python ask.py      (type 'exit' to quit, '/reset' to start over)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src import config
from src.agent import SupportAgent

config.setup_logging()
agent = SupportAgent()
print("Router support agent. Type 'exit' to quit.")
while True:
    try:
        query = input("\nYou: ").strip()
    except (EOFError, KeyboardInterrupt):
        break
    if query.lower() in ("exit", "quit"):
        break
    if query == "/reset":
        agent = SupportAgent()
        print("(conversation reset)")
        continue
    reply = agent.chat(query)
    print(f"\nBot: {reply['answer']}")
    print(f"     [action={reply['action']} confidence={reply['confidence']}"
          + (f" ticket={reply['ticket_id']}" if reply["ticket_id"] else "") + "]")
