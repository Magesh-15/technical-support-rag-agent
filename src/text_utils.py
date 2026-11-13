"""Small text helpers shared by the embedder and the agent."""
import re

STOPWORDS = set(
    """a an the and or but if is are was were be been am do does did how what why when where which who
    i me my we our you your it its this that these those to of in on at for with from by as can could
    would should will just so not no yes please about into out up down get got have has had""".split()
)
_word = re.compile(r"[a-z0-9]+")


def normalize(text):
    return text.lower().replace("wi-fi", "wifi").replace("wi fi", "wifi")


def content_words(text):
    """Meaningful words only (no stopwords)."""
    return [w for w in _word.findall(normalize(text)) if w not in STOPWORDS]


def stem(word):
    for suffix in ("ing", "ed", "es", "s"):
        if len(word) > len(suffix) + 2 and word.endswith(suffix):
            return word[: -len(suffix)]
    return word


def tokenize(text):
    return [stem(w) for w in content_words(text)]
