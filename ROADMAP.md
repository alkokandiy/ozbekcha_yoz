# Roadmap

Where Özbekcha Yoz could go next, in the order that gets the most use out of
the least new risk. Nothing here is committed to; it is a map, not a promise.

The thing to protect at every step: **the bot changes four character patterns
and nothing else.** Every feature below is judged by whether a journalist can
paste a finished article into it and trust that their words came back
untouched. The day it "improves" a word nobody asked it to touch, it stops
being usable for real work.

---

## Phase 0 — Addresses are protected (done)

Links were being corrupted: `example.com/schools/chat` came back as
`example.com/sçools/çat`. `sch` and `ch` are everywhere in URLs, and the
damage was silent — the prose read correctly and only the link was dead.

The rule now is **words versus addresses**:

| | behaviour | why |
|---|---|---|
| URLs, `www.` and bare hosts (`t.me/kanal`) | untouched | a changed path is a 404 |
| email addresses | untouched, local part included | a changed address bounces |
| `@mentions` | untouched | Telegram handles cannot contain ö/ğ/ş/ç at all |
| `#hashtags` | **converted** | a hashtag is a word the author wrote |

The hashtag split is deliberate. Telegram accepts `#çoyxona` perfectly well,
and a channel moving to the new alphabet wants its tags moved with it; an
@mention converted the same way just points at nobody.

Implemented inside the single pass rather than as a pre-filter: the
alternation matches an address *before* anything inside it can match, and
returns it verbatim. So the one-pass guarantee still holds, and
`ischi https://a.uz/ischi ischi` converts the prose on both sides while
leaving the middle alone.

A bare host is only recognised when it ends in a known TLD, which is what
stops a missing space after a full stop (`keldim.Shunda`) from being read as
a domain. `TLDS` in `converter.py` is the list to extend.

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

**This is not about Uzbek spelling.** There is no claim here that `sh` or `ch`
sometimes aren't digraphs — the only case where they aren't is a separator
apostrophe (`is'hoq`), and that already works. The problem is how `.docx`
stores text, and it would hit an English or Turkish converter identically.

A `.docx` paragraph is not a string. It is a list of *runs*, and Word splits
runs wherever formatting changes — and also, unhelpfully, wherever it feels
like it after spell-check, tracked changes, or an editing session. The word
`Shahar`, in one unbroken sentence with no formatting anywhere, can be stored
as:

```xml
<w:r><w:t>S</w:t></w:r><w:r><w:t>hahar</w:t></w:r>
```

Nothing in the document looks split. Only the XML is. Converting run by run
then sees `S` with no `h` after it, so the digraph never matches, and the
document comes back half-converted — worse than untouched, because nobody can
see which half.

The fix is exactly the "good algorithm" to use: don't convert runs. For each
paragraph, concatenate the runs into one string, convert that string, then
write the result back across the runs by character offset, so every run keeps
its own bold, italic, size and colour. Lengths shift (`o'` is two characters,
`ö` is one), so writing back is offset arithmetic rather than a zip.

Needs a test fixture containing a deliberately run-split word. Build it by
saving a file out of real Word with tracked changes, not by hand — hand-built
XML will be too tidy to catch the bug.

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

### 2.5 `.pdf` — out of scope, by decision

PDF has no text model to edit, only glyphs at coordinates, so converting one
faithfully means re-typesetting it. Not attempted.

If it is ever asked for, the only honest version is: extract the text, return
`.txt` or `.docx`, and say plainly that the layout is gone.

### 2.6 Scripts and code — dropped

Converting a source file wholesale rewrites identifiers: `search` becomes
`searç`, `choice` becomes `çoice`, and the file stops running while still
looking plausible in a diff. Doing it properly needs a per-language tokeniser
that converts string literals and comments only — a lot of machinery for a
handful of users.

Dropped. If someone genuinely needs it, they can convert the strings by hand.

### 2.7 Limits and privacy, stated in `/help`

Telegram caps bot downloads at 20 MB and uploads at 50 MB, so the ceiling is
20 MB in. Everything should be processed **in memory and never written to
disk** — no retention, nothing to leak, nothing to subpoena. For journalists
sending unpublished drafts through a stranger's bot, that sentence in `/help`
is a feature, and it is only true if it is designed in from the first file
handler rather than retrofitted.

---

## Phase 3 — Cyrillic to new Latin

Promoted. My first draft of this section over-weighted the ambiguity, on the
strength of general transliteration problems rather than how Uzbek Cyrillic is
actually written: **ъ and ь are not used in practice, and е/ye is not the
obstacle I made it out to be.** That removes most of what made this look
expensive.

What it needs is a direct table into the *new* alphabet, not a detour through
the old one:

```
ў → ö    ғ → ğ    ш → ş    ч → ç    қ → q
ҳ → h    х → x    ж → j    й → y    ц → s
```

Note that `ў → ö` and `ш → ş` land on the new letters in one step. Converting
Cyrillic to the old Latin first, then running it through this bot, would be
two lossy steps where one exact one will do.

The parts that still need a decision from someone who writes Uzbek
professionally, rather than a rule I invent:

- **ё, ю, я** expand to two letters (`yo`, `yu`, `ya`), so they change the
  length of the word — fine, but it means this cannot share the simple
  one-character substitution machinery.
- **ц** is `s` in `сирк`-type words and `ts` in some borrowings. Pick one
  default, list the exceptions.
- **щ** is rare but real: `şç`.
- **Proper nouns** have conventional spellings that any rule set will
  occasionally override. This is the only place the output needs reviewing.

So: a direct table, a separate `/kirill` command so nobody gets it by
accident, and a corpus of real paragraphs checked by eye before it ships.
Still the largest audience available — older writers, archives, and the body
of Cyrillic text that has to move eventually.

## Phase 4 — Reach

- **Group and channel mode.** In groups, reply only when mentioned or replied
  to; a bot that converts every message is a bot that gets removed. For
  channels, an admin-bot mode that converts posts as they are published is the
  feature channel owners will ask for by name.
- **A web page.** The converter is 60 lines of regex and ports to JavaScript
  in an afternoon: a paste box at a URL, no install, no Telegram account,
  works from a desktop newsroom. It also gives the project something to be
  found by in search, which a bot cannot be.
- **Interface languages.** The bot's own `/start` and `/help` in new-alphabet
  Uzbek, old-alphabet Uzbek, Russian and English — the people most in need of
  the tool are the least likely to read the new alphabet comfortably yet.
- **A Dockerfile.** Railway is fine, but one file makes the bot portable to
  any host, which matters if free tiers change.

### 4.1 Donations

A `/homiylik` (or `/donat`) command, as the only thing the bot ever asks for.
Two options, and they are not equivalent:

- **A payment page** (tirikchilik.uz or similar) — a link, no personal data in
  the bot, and the page handles its own receipts.
- **A card number**, 16 digits, printed on request. Simplest thing that works,
  and normal practice in Uzbekistan.

If it is a card number: put it in an environment variable
(`DONATION_CARD`), never in the source, so the repo stays public and the
number can change without a commit — and use a card that is fine to publish,
since anything a bot prints is effectively public. A card number alone can
only *receive*. Nothing else belongs anywhere near this bot: no expiry date,
no CVV, no SMS codes, and no form that collects them. The bot's answer to
`/homiylik` should be the number and nothing more.

Everything else stays free with no limits. The point of donations is to cover
a server if the free tier ever ends, not to gate anything.

### 4.2 The privacy line

Keep the `/help` wording as it is, including the second half:

> Hiç narsa saqlanmaydi. Birinçidan, maxfiylik muhim. Ikkinçidan,
> dasturçida şunça matnni saqlab turadigan server olişga pul yöq.

It is funnier than a privacy policy and more credible than one, because the
second reason is checkable. The commitment is real either way: files are
processed in memory and never written to disk, which is only true if it is
designed in from the first file handler rather than retrofitted.

Deliberately **not** on the list: accounts, message history, a database,
analytics on message content, or paid tiers. The bot's value is that it is
instant, free and keeps nothing.

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

Keep: the run-offset redistribution in 2.1, the Cyrillic table and its
exception list in Phase 3, anything touching the donation command, and all
review. These are the places where a plausible-looking wrong answer survives
a passing test.
