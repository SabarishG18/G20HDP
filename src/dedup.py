"""
dedup.py

Collapses near-duplicate stories (the same event reported by several outlets, common
with the Google News feeds) into one primary item. The primary keeps the full entry;
the other outlets are attached as `also` so they can be shown as "also covered by" links.
"""

import re

_STOPWORDS = {
    "the", "a", "an", "to", "of", "in", "on", "for", "and", "as", "at", "by",
    "with", "from", "is", "are", "new", "its", "it", "this", "that", "has",
    "have", "will", "amid", "over", "after", "says", "say",
}


def _tokens(title):
    # Drop the trailing " - Outlet" / " | Outlet" that Google News appends.
    title = re.sub(r"\s+[-|]\s+[^-|]+$", "", title)
    words = re.findall(r"[a-z0-9]+", title.lower())
    return {w for w in words if len(w) > 2 and w not in _STOPWORDS}


def _same_story(a, b, threshold=0.35):
    """True if two headlines share enough significant words (Jaccard overlap)."""
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return False
    return len(ta & tb) / len(ta | tb) >= threshold


def deduplicate(items):
    """Return one primary item per story. Each primary carries an `also` list of the
    other items covering the same story. Native feeds are preferred as the primary."""
    # Sort native-feed items first so they become the primary over Google News copies.
    items = sorted(items, key=lambda it: "news.google.com" in it["link"])

    primaries = []
    for it in items:
        for p in primaries:
            if _same_story(it["title"], p["title"]):
                p["also"].append(it)
                break
        else:
            it["also"] = []
            primaries.append(it)
    return primaries
