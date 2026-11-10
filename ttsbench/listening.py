"""Statistics for human right/wrong listening verdicts (stdlib only)."""
from math import comb, sqrt


def wilson(wrong: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval for an error proportion."""
    if n == 0:
        return float("nan"), float("nan")
    p = wrong / n
    centre = p + z * z / (2 * n)
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    denom = 1 + z * z / n
    return max(0.0, (centre - half) / denom), min(1.0, (centre + half) / denom)


def mcnemar_exact(only_a_wrong: int, only_b_wrong: int) -> float:
    """Two-sided exact McNemar p-value for paired right/wrong verdicts.

    Only sentences where exactly one of the two systems was wrong carry
    information; under the null they split 50/50.
    """
    n = only_a_wrong + only_b_wrong
    if n == 0:
        return 1.0
    k = min(only_a_wrong, only_b_wrong)
    tail = sum(comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)
