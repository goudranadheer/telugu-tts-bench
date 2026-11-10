"""Bootstrap confidence intervals over sentences."""
import random

from .metrics import error_rate


def bootstrap_ci(pairs, n_boot=2000, alpha=0.05, seed=0):
    """CI for a corpus-level error rate. `pairs` = [(edits, ref_len), ...]."""
    rng = random.Random(seed)
    n = len(pairs)
    stats = sorted(
        error_rate([pairs[rng.randrange(n)] for _ in range(n)]) for _ in range(n_boot)
    )
    return stats[int(alpha / 2 * n_boot)], stats[int((1 - alpha / 2) * n_boot) - 1]


def paired_bootstrap(pairs_a, pairs_b, n_boot=2000, seed=0):
    """Compare two systems on the SAME sentences, in the same order.

    Returns (rate_a - rate_b, CI low, CI high, p) where p is the share of
    resamples in which A is not better (lower) than B.
    """
    assert len(pairs_a) == len(pairs_b), "systems must cover the same sentences"
    rng = random.Random(seed)
    n = len(pairs_a)
    diffs = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        diffs.append(
            error_rate([pairs_a[i] for i in idx]) - error_rate([pairs_b[i] for i in idx])
        )
    diffs.sort()
    observed = error_rate(pairs_a) - error_rate(pairs_b)
    p = sum(d >= 0 for d in diffs) / n_boot
    return observed, diffs[int(0.025 * n_boot)], diffs[int(0.975 * n_boot) - 1], p
