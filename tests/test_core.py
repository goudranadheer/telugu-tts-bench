from ttsbench.metrics import edit_counts, error_rate, levenshtein
from ttsbench.normalize import aksharas, normalize
from ttsbench.stats import bootstrap_ci, paired_bootstrap


def test_normalize_strips_punct_joiners_and_maps_digits():
    assert normalize("పోస్ట్‌పోన్  చేద్దాం!") == "పోస్ట్పోన్ చేద్దాం"
    assert normalize("ధర ₹౪౫౦.") == "ధర 450"
    assert normalize("Meeting, రేపు?") == "meeting రేపు"


def test_aksharas_keep_conjuncts_together():
    assert aksharas("స్త్రీ") == ["స్త్రీ"]
    assert aksharas("విద్యార్థులు") == ["వి", "ద్యా", "ర్థు", "లు"]
    assert aksharas("అమ్మ ఇంటికి") == ["అ", "మ్మ", "ఇం", "టి", "కి"]
    assert aksharas("పోస్ట్") == ["పో", "స్ట్"]  # trailing virama stays attached


def test_levenshtein():
    assert levenshtein(list("abc"), list("abc")) == 0
    assert levenshtein(list("abc"), list("axc")) == 1
    assert levenshtein(list("abc"), list("ac")) == 1
    assert levenshtein([], list("ab")) == 2


def test_edit_counts_ignore_punctuation_and_use_units():
    assert edit_counts("అమ్మ వచ్చింది.", "అమ్మ వచ్చింది", "word") == (0, 2)
    assert edit_counts("అమ్మ వచ్చింది", "అమ్మ వచ్చాడు", "word") == (1, 2)
    e, n = edit_counts("అమ్మ వచ్చింది", "అమ్మ వచ్చాడు", "akshara")
    assert (e, n) == (2, 5)


def test_error_rate_is_corpus_level():
    assert error_rate([(1, 2), (0, 8)]) == 0.1


def test_bootstrap_ci_brackets_the_estimate():
    pairs = [(i % 3, 10) for i in range(60)]
    lo, hi = bootstrap_ci(pairs, n_boot=500)
    assert lo <= error_rate(pairs) <= hi


def test_paired_bootstrap_detects_clear_winner():
    good = [(0, 10)] * 50
    bad = [(3, 10)] * 50
    diff, lo, hi, p = paired_bootstrap(good, bad, n_boot=500)
    assert diff < 0 and hi < 0 and p == 0.0


def test_wilson_and_mcnemar():
    from ttsbench.listening import mcnemar_exact, wilson

    lo, hi = wilson(5, 10)
    assert 0.23 < lo < 0.24 and 0.76 < hi < 0.77
    assert wilson(0, 10)[0] == 0.0 and wilson(0, 10)[1] > 0.2
    assert mcnemar_exact(0, 0) == 1.0
    assert mcnemar_exact(5, 5) == 1.0
    assert abs(mcnemar_exact(0, 6) - 2 / 64) < 1e-12
