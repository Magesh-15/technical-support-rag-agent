"""Step 4: the agent. It decides what to do with each message using four tools:

    search_docs            -> find relevant chunks
    ask_clarifying_question-> ask for more detail when the message is too vague
    create_ticket          -> save a support ticket
    escalate_to_human      -> ticket + hand-off message when the bot cannot solve it

Routing is rule-based on purpose: it is predictable, free, and works with small LLMs.
The LLM is used for two things only: rewriting follow-up questions and writing answers.
"""
import logging
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config, storage
from src.generate import NOT_FOUND_TEXT, generate_answer, rewrite_query
from src.retrieve import get_retriever
from src.text_utils import content_words

log = logging.getLogger(__name__)

INJECTION = re.compile(
    r"ignore (all |any |the |your )?(previous|prior|above|earlier)?\s*(instructions|rules|prompts?)"
    r"|disregard .{0,30}(instructions|rules)|system prompt|reveal .{0,30}(prompt|instructions)"
    r"|you are now|jailbreak|developer mode|pretend (to be|you are)|forget (everything|your instructions)",
    re.I,
)
RELEVANCE_MARGIN = 0.25
GREETING = re.compile(r"^\s*(hi|hello|hey|hii|good (morning|afternoon|evening)|thanks?|thank you)\W*$", re.I)
VAGUE = re.compile(
    r"^\s*(help( me)?|(it'?s |it is )?(not )?working|(wifi|internet|router) (problem|issue|trouble)s?"
    r"|(i have )?(a )?problem|something('?s| is) wrong|not working)\W*$", re.I)
ESCALATE_STRONG = re.compile(
    r"(talk|speak|connect me) to (a |an |some)?(human|person|agent|someone|support|technician)"
    r"|human (agent|support)|(create|raise|open|make|file|need) (me )?(a |the )?(support )?ticket|escalate|real person", re.I)
ESCALATE_WEAK = re.compile(  # only counts when we already gave an answer earlier
    r"nothing (has )?(worked|works|helped|helps)|(didn'?t|did not|doesn'?t|does not|won'?t) (work|help|fix)"
    r"|still (not working|broken|the same|happening|failing)|this is (useless|frustrating)|waste of time", re.I)
AFFIRM = re.compile(r"^\s*(yes|yeah|yep|yup|sure|ok|okay|please|y|create( it)?|go ahead|do it)\b", re.I)
NEGATE = re.compile(r"^\s*(no|nope|nah|n|not now|no thanks)\b", re.I)

CLARIFY_TEXT = ("Could you tell me a bit more? What exactly is happening (for example: no internet, "
                "slow speed, Wi-Fi dropping, a blinking or red light) and which router model are you using?")
GREETING_TEXT = ("Hello! I'm the router support assistant. Tell me what's going wrong "
                 "(for example: \"Wi-Fi keeps disconnecting\" or \"how do I reset my router\").")
INJECTION_TEXT = "I can only help with home Wi-Fi router support, so I can't follow that request. What router problem can I help with?"


# ---------- tools ----------
def search_docs(query, retriever=None, k=None):
    return (retriever or get_retriever()).retrieve(query, k)


def ask_clarifying_question():
    return CLARIFY_TEXT


def create_ticket(summary, details):
    return storage.create_ticket(summary, details)


def escalate_to_human(summary, details):
    """Create a ticket and return the hand-off message."""
    ticket = create_ticket(summary, details)
    msg = (f"I'm sorry this isn't solved yet. I've created support ticket **{ticket['id']}** with your "
           "conversation so a human agent can follow up. Please keep that ticket number.")
    return msg, ticket


TOOLS = {
    "search_docs": search_docs,
    "ask_clarifying_question": ask_clarifying_question,
    "create_ticket": create_ticket,
    "escalate_to_human": escalate_to_human,
}


def confidence_from_distance(distance, threshold):
    """Map distance to a 0-1 score. 0.5 is exactly the 'trust' threshold."""
    return round(max(0.0, min(1.0, 1 - distance / (2 * threshold))), 2)


class SupportAgent:
    """One instance per conversation (it holds the memory)."""

    def __init__(self, retriever=None):
        self.retriever = retriever or get_retriever()
        self.history = []            # [{"role": "user"|"assistant", "content": str}]
        self.pending_ticket = None   # set after we offer to create a ticket
        self.pending_clarify = None  # original vague message we asked about
        self.last_question = ""

    # ---- helpers ----
    def _reply(self, action, answer, sources=None, confidence=0.0, ticket_id=None):
        return {"answer": answer, "sources": sources or [], "confidence": confidence,
                "ticket_id": ticket_id, "action": action}

    def _remember(self, user, assistant):
        self.history += [{"role": "user", "content": user}, {"role": "assistant", "content": assistant}]
        self.history = self.history[-2 * config.MAX_HISTORY_TURNS:]

    def _transcript(self, extra=""):
        lines = [f"{m['role']}: {m['content']}" for m in self.history]
        if extra:
            lines.append(f"user: {extra}")
        return "\n".join(lines)

    def _open_ticket(self, summary, message, reason):
        msg, ticket = escalate_to_human(summary, f"Reason: {reason}\n\n{self._transcript(message)}")
        self._remember(message, msg)
        log.info("Ticket %s created (%s)", ticket["id"], reason)
        return self._reply("ticket_created", msg, ticket_id=ticket["id"])

    # ---- main entry ----
    def chat(self, message):
        message = (message or "").strip()[: config.MAX_MESSAGE_CHARS]
        if not message:
            return self._reply("empty", "Please type your question, for example: \"Wi-Fi keeps disconnecting\".")
        if INJECTION.search(message):
            log.warning("Possible prompt injection blocked: %r", message[:100])
            return self._reply("refused", INJECTION_TEXT)
        if GREETING.match(message) and not self.pending_ticket:
            return self._reply("greeting", GREETING_TEXT)

        # 1) answer to "Would you like me to create a ticket?"
        if self.pending_ticket:
            pending, self.pending_ticket = self.pending_ticket, None
            if AFFIRM.match(message):
                return self._open_ticket(pending, message, "user accepted ticket offer")
            if NEGATE.match(message):
                msg = "Okay. Ask me anything else about your router."
                self._remember(message, msg)
                return self._reply("answer", msg)

        # 2) user is frustrated or asks for a human
        if ESCALATE_STRONG.search(message) or (self.history and ESCALATE_WEAK.search(message)):
            return self._open_ticket(self.last_question or message, message, "user asked for escalation / nothing worked")

        # 3) vague message -> ask a clarifying question (once)
        if self.pending_clarify:
            text, self.pending_clarify = f"{self.pending_clarify}. {message}", None
        else:
            text = message
            if not self.history and (VAGUE.match(message) or len(content_words(message)) <= 1):
                self.pending_clarify = message
                return self._reply("clarify", ask_clarifying_question())

        # 4) rewrite follow-ups, then search
        search_query = rewrite_query(text, self.history) if self.history else text
        chunks = search_docs(search_query, self.retriever)
        threshold = self.retriever.threshold
        best = chunks[0]["distance"] if chunks else 99.0
        confidence = confidence_from_distance(best, threshold)
        log.info("q=%r rewritten=%r best_distance=%.3f", message, search_query, best)

        # 5) low confidence -> do not call the LLM, offer a ticket
        if not chunks or best > threshold:
            self.pending_ticket = text
            self._remember(message, NOT_FOUND_TEXT)
            return self._reply("not_found", NOT_FOUND_TEXT, confidence=confidence)
            chunks = [c for c in chunks if c["distance"] <= best + RELEVANCE_MARGIN][:3]
           

        # 6) answer from the documents
        answer = generate_answer(search_query, chunks)
        self.last_question = text
        if "couldn't find this in the documentation" in answer.lower():
            self.pending_ticket = text
            self._remember(message, answer)
            return self._reply("not_found", answer, confidence=min(confidence, 0.3))

        seen, sources = set(), []
        for c in chunks:
            if c["title"] not in seen:
                seen.add(c["title"])
                body = c["text"].split("\n", 1)[-1]
                sources.append({"title": c["title"], "source": c["source"],
                                "snippet": body[:300], "distance": round(c["distance"], 3)})
        self._remember(message, answer)
        return self._reply("answer", answer, sources, confidence)
