# Roadmap

Where Özbekcha Yoz could go next, in the order that gets the most use out of
the least new risk. Nothing here is committed to; it is a map, not a promise.

The thing to protect at every step: **the bot changes four character patterns
and nothing else.** Every feature below is judged by whether a journalist can
paste a finished article into it and trust that their words came back
untouched. The day it "improves" a word nobody asked it to touch, it stops
being usable for real work.

---

## Phase 0 — A defect, found while checking this roadmap's claims

Links are corrupted:

```
https://example.com/schools/chat?id=5
  ->  https://example.com/sçools/çat?id=5
```

`sch` and `ch` occur constantly in URLs, and a converted URL is a dead URL.
This is not theoretical for the stated audience: journalists, channel owners
and bloggers paste posts that contain links, and the damage is silent — the
text reads correctly and only the link is broken.

The same applies to anything that is a machine identifier rather than prose:

| | why it must not convert |
|---|---|
| URLs (`http://`, `https://`, `www.`, bare domains) | a changed path is a 404 |
| email addresses | a changed address does not deliver |
| `@mentions` | Telegram usernames cannot contain ö/ğ/ş/ç at all |
| `#hashtags` | a converted tag is a *different* tag, splitting an audience |

Hashtags are the arguable one — a channel moving to the new alphabet may well
want its tags converted too — so that should be a setting, with "leave them
alone" as the default. URLs, emails and mentions are not arguable.

The fix is to tokenise before substituting: split the text on URL / email /
mention patterns, convert only the prose between them, and reassemble. This
keeps the single-pass guarantee and is maybe 20 lines plus tests, but it is
the first change that makes the converter more than one regex, so it needs
the corpus from 1.3 to protect it.

Until it ships, `/help` should say that links are converted too, so nobody
loses a URL without warning.

---

## Phase 1 — Cheap wins, no new failure modes

### 1.1 Reverse conversion (new → old)

Ö→O', Ğ→G', Ş→Sh, Ç→Ch. The mapping is one-to-one in both directions, so
this is the same regex with the table flipped — perhaps 30 lines including
tests.

Worth more than it sounds: during a transition, people have to *publish into*
systems that cannot render Ö/Ğ/Ş/Ç — old CMSes, government forms, SMS
gateways, fonts without the glyphs. Writing in the new alphabet and converting
down on the way out is the workflow that makes adopting it possible at all.

Surface it as `/eski` (or a button under the reply), never as autodetection.
Guessing the direction will eventually guess wrong on a mixed document.

### 1.2 Plain-text files: `.txt`, `.srt`, `.vtt`, `.csv`, `.md`

Read, convert, send back with the same filename. No parsing, no formatting
model, no library — the converter already handles the whole content.

Two details that decide whether this works in practice:

- **Encoding.** Files from the Cyrillic era arrive as cp1251 or koi8, not
  UTF-8, and `str.decode` will either throw or produce mojibake. Detect, and
  when detection is uncertain, say so instead of returning garbage.
- **Subtitles are the sleeper feature.** `.srt` carries timestamps that must
  survive byte-for-byte. The converter never touches digits, `:`, `-` or `>`,
  so `00:01:23,456 --> 00:01:25,120` passes through untouched already. Video
  people re-type subtitle files by hand today.

### 1.3 CI and a golden corpus

GitHub Actions running the suite on 3.12 and 3.13 on every push.

More valuable: a corpus test. Twenty real paragraphs — news articles, a legal
notice, a poem, a recipe, a code comment — each with a reviewed expected
output, in `tests/corpus/`. Unit tests prove the regex does what I think;
a corpus proves what I think is right. Every bug found later gets a line
added, so it can never come back.

---

## Phase 2 — Office documents

This is the feature people will actually ask for, and the only one with a real
correctness trap in it.

### 2.1 The run-splitting problem — read this before writing any code

A `.docx` paragraph is not a string. It is a list of *runs*, and Word splits
runs wherever formatting changes — and also, unhelpfully, wherever it feels
like it after spell-check, tracked changes, or editing history. The word
`Shahar` can legitimately be stored as:

```
run1: "S"   run2: "hahar"
```

Converting run by run then sees `S` with no `h` after it, and the digraph
never matches. The document comes back half-converted, which is worse than
not converted, because nobody can see which half.

The fix: work at paragraph level. Concatenate the runs, convert the whole
string, then write the result back across the runs — redistributing by
character offset so each run keeps its own bold, italic, size and colour.
Lengths shift (`o'` is two characters, `ö` is one), so the mapping back is
offset arithmetic, not a zip.

This is the one piece of this roadmap I would not delegate, and the one that
needs a test fixture with deliberately split runs.

### 2.2 `.docx` — python-docx

Beyond paragraphs, the text that must not be missed: tables, headers and
footers, footnotes, endnotes, text boxes, hyperlink display text, comments,
and the document title in the properties. A converter that handles body text
and silently skips tables will embarrass someone in a meeting.

### 2.3 `.xlsx` — openpyxl

Convert string cell values. Leave numbers, dates and booleans alone.

The trap is formulas. `=CONCATENATE("Shahar: ", A1)` has a string literal
inside it that should convert, while the function name must not — and a cell
whose value *looks* like text may be a cached formula result that Excel will
recompute and overwrite. Convert formula string literals only, or skip
formula cells entirely in v1 and report how many were skipped.

Also: sheet names, defined names, and data-validation dropdown lists are text
users expect to be converted.

### 2.4 `.pptx` — python-pptx

Same run problem as `.docx`, same solution. Slide text, speaker notes, tables,
chart labels, SmartArt.

### 2.5 `.pdf` — be honest about this one

PDF has no text model to edit; it has glyphs at coordinates. Converting a PDF
faithfully means re-typesetting it, and the result will not match the original
layout. Promising "send a PDF, get a PDF" leads to complaints.

What to offer instead: extract the text and return `.txt` or `.docx`, stating
plainly that layout is lost. That is still useful — people want the words back
so they can re-lay them out themselves.

### 2.6 Scripts and code — convert strings and comments only

"Fix my script the same way" is a reasonable request with an unreasonable
literal reading. Blanket-converting a `.py` or `.js` file rewrites identifiers
and keywords: `search` becomes `searç`, `choice` becomes `çoice`, and the file
no longer runs. Worse, it looks fine in a diff to anyone not reading closely.

The useful behaviour is to convert **string literals and comments only**,
leaving code untouched — a tokeniser-level job, per language, not a regex one.
Until that exists, a code file should get a warning and a plain-text
conversion the user has to opt into, not a silent rewrite.

### 2.7 Limits and privacy, stated in `/help`

Telegram caps bot downloads at 20 MB and uploads at 50 MB, so the ceiling is
20 MB in. Everything should be processed **in memory and never written to
disk** — no retention, nothing to leak, nothing to subpoena. For journalists
sending unpublished drafts through a stranger's bot, that sentence in `/help`
is a feature, and it is only true if it is designed in from the first file
handler rather than retrofitted.

---

## Phase 3 — Cyrillic to Latin

A different class of problem, and the largest expansion available.

Everything so far is a character substitution with no ambiguity. Cyrillic
transliteration is not: **е** is `e` or `ye` depending on position, **ё/ю/я**
expand to two letters, **ъ** and **ь** have no clean equivalent, **щ** maps to
a sequence, and proper nouns have conventional spellings that rules get wrong.
Any rule set will be about 95% right, and the remaining 5% lands in people's
names.

So it needs the Phase 1.3 corpus first, built much larger, and reviewed by
someone who writes Uzbek professionally. It should also be a clearly separate
command (`/kirill`) so nobody gets it by accident, and the output should be
presented as a draft to proofread, not a finished conversion.

The audience is real — older writers, archives, and the enormous body of
Cyrillic text that has to move eventually — but shipping it badly would
undermine trust in the part that is exact.

---

## Phase 4 — Reach

- **Group and channel mode.** In groups, reply only when mentioned or replied
  to; a bot that converts every message is a bot that gets removed. For
  channels, an admin-bot mode that converts posts as they are published is the
  feature channel owners will ask for by name.
- **A web page.** The converter is 40 lines of regex and ports to JavaScript
  in an afternoon: a paste box at a URL, no install, no Telegram account,
  works from a desktop newsroom. It also gives the project something to be
  found by in search, which a bot cannot be.
- **Interface languages.** The bot's own `/start` and `/help` in new-alphabet
  Uzbek, old-alphabet Uzbek, Russian and English — the people most in need of
  the tool are the least likely to read the new alphabet comfortably yet.
- **A Dockerfile.** Railway is fine, but one file makes the bot portable to
  any host, which matters if free tiers change.

Deliberately **not** on this list: an account system, message history, a
database, analytics on message content, or paid tiers. The bot's value is that
it is instant, free and keeps nothing. Each of those would cost that.

---

## Open questions

1. **Standard.** Confirm the final letter set against the official decree
   before making public claims about "the 2026 standard" — the mapping here is
   the four patterns as specified, and if the official set differs in any
   letter, the converter changes and the README's claims change with it.
2. **Apostrophe coverage.** `APOSTROPHES` currently lists eight characters.
   Real text from old Word documents may contain others; the corpus will show.
3. **Does anyone need `.epub`?** Publishers and archives might. Unknown.

## What to delegate

Mechanical and well-specified, with the interface already decided: the
plain-text handlers (1.2), CI (1.3), the `.xlsx` and `.pptx` walkers once the
run-redistribution helper exists (2.3, 2.4), interface translations, the
Dockerfile.

Keep: the run-offset redistribution in 2.1, the code-literal tokeniser in 2.6,
every line of the Cyrillic rules in Phase 3, and all review. These are the
places where a plausible-looking wrong answer survives a passing test.
