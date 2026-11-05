# Özbekça Yoz — notes for agents

A Telegram bot that converts old Uzbek Latin orthography (1995) to the
2023/2026 standard. Small on purpose.

## Rules

- **The conversion is a pure function.** `yoz/converter.py` has no imports
  beyond `re` and no I/O. Keep it that way: it is the one piece that must be
  testable without a token or a network.
- **No language model.** The mapping is a closed set of four patterns. Do not
  add an LLM call, an API key or a prompt.
- **Exactly four patterns**, with case and apostrophe variants: `O'`→Ö,
  `G'`→Ğ, `Sh`→Ş, `Ch`→Ç. Never touch any other letter, word, punctuation
  mark or whitespace. No spell-checking, no grammar, no normalising.
- **Replies carry only the converted text.** No greeting, no "here you go",
  no footer. `/start` and `/help` are the only chatty handlers.
- **Single pass.** The regex alternation in `_PATTERN` is applied once so
  output is never re-scanned. Do not refactor it into a chain of
  `str.replace` calls — that reintroduces the `ischi` → `işi` bug.
- **Case comes from the first character** of the match, so `SHARAF`→`ŞARAF`
  and `sHaraf`→`şaraf`.
- Send messages with `parse_mode=None`. User text is data; it must never be
  parsed as HTML or Markdown.

## Checks before any commit

```bash
python run_tests.py
```

**Never report the suite green from `python -m unittest` alone.** Without
aiogram it prints `OK (skipped=22)` and exits 0, so twenty-two tests are
reported as success while never running. `run_tests.py` fails on a skip.
If it tells you to install dependencies, install them — do not "verify" the
change by reading the skipped output.

Add a test for every behaviour change, including the edge cases
(`san'at`, `is'hoq`, `ischi`, mixed case, emojis, code fences).

## Deployment

Railway, long polling, `Procfile` worker — no web server, no port, no
webhook. Token comes from the `BOT_TOKEN` variable. Only one process may poll
a token at a time.
