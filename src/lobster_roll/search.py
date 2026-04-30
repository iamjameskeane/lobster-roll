from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any

FUZZY_THRESHOLD = 0.55  # minimum ratio to count as fuzzy match


def _normalize(text: str) -> str:
    """Lowercase and strip."""
    return text.lower().strip()


def _substring_score(query: str, text: str) -> float:
    """Return 1.0 if query is a substring of text, else 0.0."""
    if query in text:
        return 1.0
    return 0.0


def _fuzzy_score(query: str, text: str) -> float:
    """Return SequenceMatcher ratio between query and text."""
    return SequenceMatcher(None, query, text).ratio()


def _score(query: str, text: str) -> tuple[float, str]:
    """Score a query against text. Returns (score, match_type).

    Substring match (1.0) always ranks above fuzzy match.
    Fuzzy matches below FUZZY_THRESHOLD are excluded.
    """
    q = _normalize(query)
    t = _normalize(text)

    # Substring match wins
    if _substring_score(q, t) > 0:
        return (1.0, "substring")

    # Also check if query tokens are substrings of the text
    # e.g. "whole ml" against "whole milk" — "whole" is substring, "ml" is prefix of "milk"
    tokens = q.split()
    if len(tokens) > 1:
        token_hits = sum(1 for tok in tokens if tok in t)
        if token_hits == len(tokens):
            return (0.95, "token_substring")
        # Partial token substring bonus
        if token_hits > 0:
            partial = token_hits / len(tokens)
            if partial >= 0.5:
                token_score = 0.7 + (0.2 * partial)
                return (token_score, "partial_token")

    # Fuzzy match
    ratio = _fuzzy_score(q, t)
    if ratio >= FUZZY_THRESHOLD:
        return (ratio, "fuzzy")

    return (0.0, "none")


def search_items(
    query: str,
    items: list[dict[str, Any]],
    fields: list[str] | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Search items by fuzzy + substring matching on specified fields.

    Args:
        query: search string
        items: list of dicts (foods or meals)
        fields: which fields to search (default: ["id", "name"])
        limit: max results to return

    Returns:
        List of items with added "match_score" and "match_type" fields,
        sorted by score descending.
    """
    if fields is None:
        fields = ["id", "name"]

    results = []
    seen_ids: set[str] = set()

    for item in items:
        best_score = 0.0
        best_type = "none"
        for field in fields:
            text = item.get(field, "")
            if not text:
                continue
            score, match_type = _score(query, text)
            if score > best_score:
                best_score = score
                best_type = match_type

        if best_score > 0 and item.get("id") not in seen_ids:
            results.append({
                **item,
                "match_score": round(best_score, 3),
                "match_type": best_type,
            })
            seen_ids.add(item.get("id", ""))

    # Sort: substring first (score 1.0), then by score descending
    results.sort(key=lambda r: (-r["match_score"], r.get("id", "")))

    return results[:limit]
