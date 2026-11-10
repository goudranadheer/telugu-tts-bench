"""Edit-distance error rates (word, akshara, character)."""
from .normalize import normalize, tokens


def levenshtein(ref: list, hyp: list) -> int:
    """Minimum substitutions + insertions + deletions turning ref into hyp."""
    if not ref:
        return len(hyp)
    prev = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        cur = [i]
        for j, h in enumerate(hyp, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (r != h)))
        prev = cur
    return prev[-1]


def edit_counts(ref: str, hyp: str, unit: str = "akshara") -> tuple[int, int]:
    """Return (edits, reference length) after normalising both strings."""
    r = tokens(normalize(ref), unit)
    h = tokens(normalize(hyp), unit)
    return levenshtein(r, h), len(r)


def error_rate(pairs: list[tuple[int, int]]) -> float:
    """Corpus-level rate: total edits / total reference length."""
    total = sum(n for _, n in pairs)
    return sum(e for e, _ in pairs) / total if total else float("nan")
