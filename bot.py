"""Özbekça Yoz — Telegram bot.

Converts old Uzbek Latin orthography (1995) to the official 2023/2026
alphabet. The conversion itself is a pure function in ``yoz.converter``,
so the bot needs no AI model, no API key and no network beyond Telegram.

Run locally:   BOT_TOKEN=123:abc python bot.py
On Railway:    the Procfile worker starts this file.
"""

import asyncio
import logging
import os
import re
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InlineQueryResultsButton,
    InputTextMessageContent,
    Message,
)
from aiogram.utils.markdown import hbold, hcode

from yoz import convert

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("yoz.bot")

#: Telegram's hard limit for one text message.
MAX_MESSAGE = 4096

#: The FAQ page, served from docs/ by GitHub Pages.
SITE_URL = "https://alkokandiy.github.io/ozbekcha_yoz/"

#: A 16-digit card number, set as a deployment variable so it never enters
#: the repository. Git history is permanent: a number committed once stays
#: readable in the history even after it is deleted from the file.
DONATION_CARD = (os.environ.get("DONATION_CARD") or "").strip()

#: Optional holder name, which card-to-card transfers sometimes ask for.
DONATION_NAME = (os.environ.get("DONATION_NAME") or "").strip()

START_TEXT = (
    f"{hbold('Özbekça Yoz')}\n\n"
    "Eski imlodagi matnni yuboring — yangi özbek lotin alifbosiga "
    "ögirib beraman.\n\n"
    f"{hcode(chr(79) + chr(39))} → Ö "
    f"{hcode(chr(71) + chr(39))} → Ğ "
    f"{hcode('Sh')} → Ş "
    f"{hcode('Ch')} → Ç\n\n"
    "Boşqa hiç narsa özgarmaydi: tinish belgilari, qatorlar, emojilar "
    "joyida qoladi.\n\n"
    "Har qanday çatda ham işlataolasiz: "
    f"{hcode('@bot_username matn')} deb yozing.\n\n"
    f"Savollarga javoblar: {SITE_URL}"
)

HELP_TEXT = (
    f"{hbold('Qanday işlaydi')}\n\n"
    "Matn yuboring — javob sifatida faqat ögirilgan matnni olasiz.\n\n"
    f"{hbold('Ögirish jadvali')}\n"
    "O' · O’ · O` · Oʻ → Ö\n"
    "o' · o’ · o` · oʻ → ö\n"
    "G' · G’ · G` · Gʻ → Ğ\n"
    "g' · g’ · g` · gʻ → ğ\n"
    "Sh · SH → Ş sh → ş\n"
    "Ch · CH → Ç ch → ç\n\n"
    f"{hbold('Diqqat')}\n"
    "O yoki G dan keyin kelmagan tutuq belgisi özgarmaydi — "
    f"{hcode('san' + chr(39) + 'at')} şundayligida qoladi.\n\n"
    f"{hbold('Manzillar özgarmaydi')}\n"
    "Havola, pochta manzili va @nom öz holiça qoladi: ularda bitta harf "
    "özgarsa, havola öladi. #xeştag esa ögiriladi — u manzil emas, siz "
    "yozgan söz.\n\n"
    f"{hbold('Maxfiylik')}\n"
    "Hiç narsa saqlanmaydi. Birinçidan, maxfiylik muhim. Ikkinçidan, "
    "dasturçida şunça matnni saqlab turadigan server olişga pul yöq."
)

def donation_text() -> str:
    """The reply to /homiylik, or an apology when nothing is configured."""
    digits = re.sub(r"\D", "", DONATION_CARD)
    if len(digits) != 16:
        return (
            "Hozirça homiylik uçun karta qöyilmagan. "
            "Bot baribir bepul — hiç narsa özgarmaydi."
        )
    grouped = " ".join(digits[i : i + 4] for i in range(0, 16, 4))
    lines = [
        "Botdan foyda olgan bölsangiz yoki mehringiz jöşib ketayotgan "
        "bölsa — mana:\n",
        hcode(grouped),
    ]
    if DONATION_NAME:
        lines.append(f"\n{DONATION_NAME}")
    lines.append("\nRahmat.")
    return "\n".join(lines)


dp = Dispatcher()


@dp.message(CommandStart())
async def on_start(message: Message) -> None:
    me = await message.bot.me()
    await message.answer(START_TEXT.replace("bot_username", me.username or "bot"))


@dp.message(Command("help", "yordam"))
async def on_help(message: Message) -> None:
    await message.answer(HELP_TEXT)


@dp.message(Command("homiylik", "donat"))
async def on_donate(message: Message) -> None:
    await message.answer(donation_text())


@dp.message(F.text)
async def on_text(message: Message) -> None:
    await _reply_converted(message, message.text)


@dp.message(F.caption)
async def on_caption(message: Message) -> None:
    await _reply_converted(message, message.caption)


async def _reply_converted(message: Message, source: str) -> None:
    """Send the converted text and nothing else."""
    result = convert(source)
    # Conversion never lengthens text (two characters become one), so a
    # chunker is only a guard against forwarded oddities.
    for chunk in _chunks(result):
        await message.answer(chunk, parse_mode=None)


def _chunks(text: str, size: int = MAX_MESSAGE):
    if len(text) <= size:
        yield text
        return
    for start in range(0, len(text), size):
        yield text[start : start + size]


@dp.inline_query()
async def on_inline(query: InlineQuery) -> None:
    """Let the bot be used inside any chat: ``@bot matn``."""
    source = query.query
    if not source:
        await query.answer(
            [],
            cache_time=5,
            is_personal=True,
            button=InlineQueryResultsButton(
                text="Ögirmoqçi bölgan matnni yozing",
                start_parameter="start",
            ),
        )
        return

    result = convert(source)
    await query.answer(
        [
            InlineQueryResultArticle(
                id="yoz",
                title="Yangi alifboda yuborish",
                description=result[:120],
                input_message_content=InputTextMessageContent(
                    message_text=result[:MAX_MESSAGE],
                    parse_mode=None,
                ),
            )
        ],
        cache_time=0,
        is_personal=True,
    )


#: A real token is "<bot id>:<35 character secret>".
TOKEN_SHAPE = re.compile(r"^\d{5,}:[A-Za-z0-9_-]{30,}$")


def read_token() -> str:
    """Return the bot token, or exit with an explanation.

    A placeholder is rejected as firmly as a missing value. Railway offers to
    prefill variables from a committed .env.example, so "looks set but is
    nonsense" is a likelier failure than "not set at all", and Telegram's own
    answer to it is a bare 401 inside a restart loop.
    """
    for name in ("BOT_TOKEN", "TELEGRAM_BOT_TOKEN", "TELEGRAM_TOKEN"):
        token = (os.environ.get(name) or "").strip().strip('"' + "'")
        if not token:
            continue
        if not TOKEN_SHAPE.match(token):
            sys.exit(
                f"{name} is set but does not look like a Telegram token "
                f"(expected <digits>:<35 characters>, got {len(token)} "
                "characters). Replace it with the token from @BotFather."
            )
        return token
    sys.exit(
        "BOT_TOKEN is not set. Add it as a Railway variable "
        "(or export it locally) and restart."
    )


async def main(token: str) -> None:
    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    # A leftover webhook would stop long polling from ever receiving updates.
    await bot.delete_webhook(drop_pending_updates=True)
    me = await bot.me()
    log.info("starting as @%s", me.username)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    # Read the token before the event loop starts, so a bad one is reported
    # by SystemExit's own message instead of being swallowed below.
    try:
        asyncio.run(main(read_token()))
    except KeyboardInterrupt:
        log.info("stopped")
