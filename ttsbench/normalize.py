"""Telugu text normalisation and akshara (syllable) segmentation.

Both the reference text and the ASR hypothesis pass through `normalize`
before scoring, so that punctuation, invisible joiners and digit style
never count as TTS errors.
"""
import re
import unicodedata

VIRAMA = "్"
ZERO_WIDTH = dict.fromkeys(map(ord, "​‌‍﻿"), None)
TELUGU_DIGITS = {ord(chr(0x0C66 + i)): str(i) for i in range(10)}

_PUNCT = re.compile(r"[^\w\sఀ-౿]|_", re.UNICODE)
_SPACE = re.compile(r"\s+")


def _is_consonant(ch: str) -> bool:
    return "క" <= ch <= "హ" or "ౘ" <= ch <= "ౚ" or ch == "ౝ"


def _is_dependent(ch: str) -> bool:
    """Vowel signs, length marks and anusvara / visarga / candrabindu."""
    return (
        "ా" <= ch <= "ౌ"
        or ch in "ౕౖౢౣ"
        or "ఀ" <= ch <= "ఄ"
    )


def normalize(text: str) -> str:
    """NFC, strip zero-width joiners and punctuation, map Telugu digits to
    ASCII, lowercase any Latin, collapse whitespace."""
    text = unicodedata.normalize("NFC", text)
    text = text.translate(ZERO_WIDTH).translate(TELUGU_DIGITS)
    text = _PUNCT.sub(" ", text)
    return _SPACE.sub(" ", text).strip().lower()


def aksharas(text: str) -> list[str]:
    """Split normalised text into aksharas (orthographic syllables).

    An akshara is a consonant cluster joined by viramas plus its vowel sign
    and modifiers, e.g. "స్త్రీ" is one unit. Spaces are dropped. Any
    non-Telugu character is its own unit.
    """
    units: list[str] = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        j = i + 1
        if _is_consonant(ch):
            # C (virama C)* [virama]
            while j < n and text[j] == VIRAMA:
                if j + 1 < n and _is_consonant(text[j + 1]):
                    j += 2
                else:
                    j += 1
                    break
        while j < n and _is_dependent(text[j]):
            j += 1
        units.append(text[i:j])
        i = j
    return units


def tokens(text: str, unit: str) -> list[str]:
    """Tokenise normalised text for an error-rate unit."""
    if unit == "word":
        return text.split()
    if unit == "akshara":
        return aksharas(text)
    if unit == "char":
        return [c for c in text if not c.isspace()]
    raise ValueError(f"unknown unit: {unit}")
