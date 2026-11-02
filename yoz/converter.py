"""Pure text transformation: 1995 Uzbek Latin orthography -> 2023/2026 standard.

Exactly four patterns are touched, with their case and apostrophe variants:

    O' -> Ö    G' -> Ğ    Sh -> Ş    Ch -> Ç
    o' -> ö    g' -> ğ    sh -> ş    ch -> ç

Everything else — other letters, words, punctuation, line breaks, emojis,
spacing, code blocks — is returned untouched.

Addresses are left alone as well. The rule is words versus addresses: a
hashtag is a word someone wrote, so it converts, while a URL, an email
address and an @mention are machine identifiers where a changed character
means a dead link, a bounced message or a handle nobody owns.
"""

import re

#: Every character that is used in practice as the "tutuq belgisi" after O or G:
#: straight quote, curly right/left quote, backtick, modifier letter turned
#: comma (the official Oʻ/Gʻ sign), modifier letter apostrophe, acute accent
#: and prime.
APOSTROPHES = "'’‘`ʻʼ´′"

_BASE = {"o": "ö", "g": "ğ", "s": "ş", "c": "ç"}

#: Top-level domains recognised in a host written without a scheme, so that
#: "t.me/kanal" is protected while "keldim.Shunda" (a missing space, not a
#: domain) is not. Lowercase only, for the same reason. Extend as needed.
TLDS = (
    "uz|com|org|net|ru|me|io|dev|app|info|tv|news|gov|edu|co|uk|de|tr|"
    "kz|kg|tj|tm|az|biz|xyz|online|site|press|media|blog"
)

#: Characters that end a URL rather than belong to it.
_URL_STOP = r"\s<>\"'«»()\[\]"

#: Addresses, longest and most specific first. Email must precede the mention
#: rule, or "ishchi@school.uz" would be read as the mention "@school".
_KEEP = (
    # user@host.tld
    r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"
    # scheme://whatever
    r"|[A-Za-z][A-Za-z0-9+.\-]*://[^" + _URL_STOP + r"]+"
    # www.whatever
    r"|www\.[^" + _URL_STOP + r"]+"
    # bare host, with or without a path: example.com, t.me/kanal
    r"|(?:[A-Za-z0-9](?:[A-Za-z0-9\-]*[A-Za-z0-9])?\.)+(?:" + TLDS + r")"
    r"(?![A-Za-z0-9])(?:/[^" + _URL_STOP + r"]*)?"
    # @mention
    r"|@[A-Za-z0-9_]{2,}"
)

#: What actually converts.
_CONVERT = "[OoGg][" + re.escape(APOSTROPHES) + "]|[SsCc][Hh]"

#: One alternation, applied in a single left-to-right pass. An address is
#: matched before anything inside it can be, and returned verbatim, so no
#: replacement is ever re-examined by a later rule.
_PATTERN = re.compile(
    "(?P<keep>" + _KEEP + ")|(?P<convert>" + _CONVERT + ")",
    re.UNICODE,
)


def _replace(match: "re.Match[str]") -> str:
    if match.lastgroup == "keep" or match.group("keep") is not None:
        return match.group(0)
    head = match.group("convert")[0]
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
