# Özbekcha Yoz

Telegram bot that rewrites text from the old Uzbek Latin orthography (1995)
into the official updated alphabet (2023/2026 standard).

```
O' O’ O` Oʻ → Ö      Sh SH → Ş
o' o’ o` oʻ → ö      sh    → ş
G' G’ G` Gʻ → Ğ      Ch CH → Ç
g' g’ g` gʻ → ğ      ch    → ç
```

Nothing else changes. Other letters, words, grammar, punctuation, line
breaks, spacing, emojis and code blocks come back exactly as they were sent,
and the reply contains only the converted text — no greeting, no preface.

## Why there is no AI in it

The conversion is a closed set of four character patterns, so the bot does it
with one regular expression in [`yoz/converter.py`](yoz/converter.py). That
makes it instant, free to run, and identical on every input — a language model
would be slower, cost money per message, and could occasionally "improve" a
word nobody asked it to touch.

## Using it

| | |
|---|---|
| Send any text | you get the converted text back |
| Send a photo with a caption | you get the converted caption back |
| `@your_bot matn` in any chat | inline mode, converts without leaving the chat |
| `/start`, `/help` | short instructions in Uzbek |

## Deploying to Railway

1. Talk to [@BotFather](https://t.me/BotFather) → `/newbot` → copy the token.
   For inline mode also send `/setinline` and pick this bot.
2. Push this repository to GitHub.
3. On [Railway](https://railway.app): **New Project → Deploy from GitHub repo**
   and pick the repo.
4. Open the service → **Variables** → add:

   | Name | Value |
   |---|---|
   | `BOT_TOKEN` | the token from BotFather |

5. Deploy. The `Procfile` runs it as a `worker`, so no public domain, no port
   and no health check are needed — the bot connects out to Telegram by long
   polling.

Logs should end with `starting as @your_bot`. Send the bot a message to check.

`railway.json` restarts the service on failure, up to 10 times.

### Variable names

`BOT_TOKEN` is the expected name; `TELEGRAM_BOT_TOKEN` and `TELEGRAM_TOKEN`
also work. With none of them set, the process exits immediately with a message
saying so rather than crash-looping silently.

A token that is set but malformed is refused the same way, by shape, before
Telegram is contacted. This matters because Railway offers to prefill its
variables from a committed `.env.example`: a placeholder left in that file
would otherwise be deployed as though it were a real token, and Telegram's
only reply is a bare `401 Unauthorized` inside a restart loop. For that reason
`.env.example` ships with an empty value, and a test enforces that it stays
empty.

## Running it locally

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
BOT_TOKEN=123456789:AA... python bot.py
```

Use Python 3.12 or 3.13. On 3.14 the install fails, because `pydantic-core`
(an aiogram dependency) has no 3.14 wheel yet and falls back to a Rust build.
This does not affect Railway, which builds with the 3.12 pinned in
`.python-version`.

Only one copy may poll a token at a time — stop the Railway deployment (or use
a second test bot) while running locally, or Telegram will return a conflict.

## Converting without Telegram

```bash
python -m yoz "O'zbekiston - sharafli va chiroyli yurt, g'alaba bizniki!"
# Özbekiston - şarafli va çiroyli yurt, ğalaba bizniki!

python -m yoz < old.txt > new.txt
```

## Tests

No dependencies — the converter is pure standard library:

```bash
python -m unittest discover -s tests -t .
```

They cover the spec example, all three case forms, all eight apostrophe
variants, structure preservation, idempotency (converting twice changes
nothing), and the two traps worth naming:

- **`san'at`, `qal'a`, `is'hoq`** — an apostrophe that does not follow O or G
  is left alone, so a separator apostrophe never collapses `s'h` into `ş`.
- **`ischi` → `isçi`** — replacements happen in a single left-to-right pass, so
  output is never re-scanned and an `s` before a converted `ch` cannot turn
  into `ş`.

## Layout

```
bot.py              Telegram handlers, polling, startup
yoz/converter.py    the transformation (no dependencies)
yoz/__main__.py     command-line entry point
tests/              unittest suite
Procfile            worker: python -u bot.py
railway.json        Railway build and restart policy
.python-version     3.12, for the Railway builder
```
