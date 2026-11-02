"""Pure text transformation: 1995 Uzbek Latin orthography -> 2023/2026 standard.

Exactly four patterns are touched, with their case and apostrophe variants:

    O' -> Ö    G' -> Ğ    Sh -> Ş    Ch -> Ç
    o' -> ö    g' -> ğ    sh -> ş    ch -> ç

Everything else — other letters, words, punctuation, line breaks, emojis,
spacing, code blocks — is returned untouched.
"""

import re

#: Every character that is used in practice as the "tutuq belgisi" after O or G:
#: straight quote, curly right/left quote, backtick, modifier letter turned
#: comma (the official Oʻ/Gʻ sign), modifier letter apostrophe, acute accent
#: and prime.
APOSTROPHES = "'’‘`ʻʼ´′"

_BASE = {"o": "ö", "g": "ğ", "s": "ş", "c": "ç"}

#: One alternation, applied in a single left-to-right pass so that no
#: replacement can ever be re-examined by a later rule.
_PATTERN = re.compile(
    "[OoGg][" + re.escape(APOSTROPHES) + "]|[SsCc][Hh]",
    re.UNICODE,
)


def _replace(match: re.Match) -> str:
    head = match.group(0)[0]
    letter = _BASE[head.lower()]
    return letter.upper() if head.isupper() else letter


def convert(text: str) -> str:
    """Return ``text`` with the four legacy digraphs replaced.

    The case of the *first* character decides the case of the result, so
    ``SHARAF`` -> ``ŞARAF``, ``Sharaf`` -> ``Şaraf``, ``sharaf`` -> ``şaraf``.

    An apostrophe that does not follow O or G is left alone, which is what
    keeps separator apostrophes such as ``is'hoq`` from collapsing into ``ş``.
    """
    if not text:
        return text
    return _PATTERN.sub(_replace, text)
