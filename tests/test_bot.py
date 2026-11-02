"""Handler-level tests with stubbed Telegram objects.

Skipped when aiogram is not installed, so the converter suite still runs on a
bare interpreter. Run them with the deployment interpreter:

    python -m unittest discover -s tests -t .
"""

import contextlib
import os
import unittest

try:
    import bot as bot_module
except ModuleNotFoundError as exc:  # pragma: no cover - aiogram absent
    bot_module = None
    _REASON = f"aiogram not installed ({exc.name})"


class StubMessage:
    """Captures what a handler would send instead of calling Telegram."""

    def __init__(self, text=None, caption=None):
        self.text = text
        self.caption = caption
        self.sent = []

    async def answer(self, text, **kwargs):
        self.sent.append((text, kwargs))


class StubInlineQuery:
    def __init__(self, query):
        self.query = query
        self.answered = None

    async def answer(self, results, **kwargs):
        self.answered = (results, kwargs)


@unittest.skipIf(bot_module is None, "aiogram not installed")
class TestTextHandler(unittest.IsolatedAsyncioTestCase):
    async def test_reply_is_only_the_converted_text(self):
        message = StubMessage(text="Salom, O'zbekiston! Shahar chiroyli.")
        await bot_module.on_text(message)
        self.assertEqual(len(message.sent), 1)
        text, kwargs = message.sent[0]
        self.assertEqual(text, "Salom, Özbekiston! Şahar çiroyli.")
        # User text must never be parsed as HTML or Markdown.
        self.assertIsNone(kwargs["parse_mode"])

    async def test_caption_is_converted(self):
        message = StubMessage(caption="g'isht")
        await bot_module.on_caption(message)
        self.assertEqual(message.sent[0][0], "ğişt")

    async def test_oversized_text_is_split(self):
        message = StubMessage(text="a" * (bot_module.MAX_MESSAGE + 10))
        await bot_module.on_text(message)
        self.assertEqual(len(message.sent), 2)
        self.assertEqual(len(message.sent[0][0]), bot_module.MAX_MESSAGE)
        self.assertEqual(len(message.sent[1][0]), 10)


@unittest.skipIf(bot_module is None, "aiogram not installed")
class TestInlineHandler(unittest.IsolatedAsyncioTestCase):
    async def test_query_returns_converted_result(self):
        query = StubInlineQuery("Choy ichdim, o'rtoq")
        await bot_module.on_inline(query)
        results, _ = query.answered
        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].input_message_content.message_text,
            "Çoy içdim, örtoq",
        )
        self.assertIsNone(results[0].input_message_content.parse_mode)

    async def test_empty_query_offers_the_prompt_button(self):
        query = StubInlineQuery("")
        await bot_module.on_inline(query)
        results, kwargs = query.answered
        self.assertEqual(results, [])
        self.assertIsNotNone(kwargs["button"])


@unittest.skipIf(bot_module is None, "aiogram not installed")
class TestTokenReading(unittest.TestCase):
    def test_each_accepted_variable_name(self):
        valid = "123456789:" + "A" * 35
        with self._clean_env() as names:
            for name in names:
                os.environ[name] = f"  {valid}  "
                self.assertEqual(bot_module.read_token(), valid)
                del os.environ[name]

    def test_missing_token_exits(self):
        with self._clean_env():
            with self.assertRaises(SystemExit):
                bot_module.read_token()

    def test_placeholder_token_is_rejected(self):
        # The value that .env.example used to carry, and that Railway will
        # happily prefill into a real deployment.
        for junk in (
            "123456789:AAExampleTokenReplaceMe",
            "your-token-here",
            "changeme",
            "123456789",
        ):
            with self._clean_env():
                os.environ["BOT_TOKEN"] = junk
                with self.assertRaises(SystemExit) as caught:
                    bot_module.read_token()
                self.assertIn("does not look like", str(caught.exception))

    def test_quoted_token_is_unwrapped(self):
        valid = "123456789:" + "A" * 35
        with self._clean_env():
            os.environ["BOT_TOKEN"] = f'"{valid}"'
            self.assertEqual(bot_module.read_token(), valid)

    @contextlib.contextmanager
    def _clean_env(self):
        import os

        names = ("BOT_TOKEN", "TELEGRAM_BOT_TOKEN", "TELEGRAM_TOKEN")
        saved = {n: os.environ.pop(n, None) for n in names}
        try:
            yield names
        finally:
            for name in names:
                os.environ.pop(name, None)
            for name, value in saved.items():
                if value is not None:
                    os.environ[name] = value


@unittest.skipIf(bot_module is None, "aiogram not installed")
class TestStaticTexts(unittest.TestCase):
    def test_help_and_start_use_the_new_alphabet(self):
        for text in (bot_module.START_TEXT, bot_module.HELP_TEXT):
            body = text
            # The mapping table legitimately shows old forms on the left side,
            # so only check the prose lines.
            prose = [
                line
                for line in body.splitlines()
                if "→" not in line and "<code>" not in line
            ]
            self.assertTrue(any("ö" in line or "ş" in line or "ç" in line for line in prose))


if __name__ == "__main__":
    unittest.main()


@unittest.skipIf(bot_module is None, "aiogram not installed")
class TestDonation(unittest.TestCase):
    """The card number lives in a deployment variable, never in the repo:
    git history is permanent, so a number committed once stays readable."""

    def _text(self, card, name=""):
        saved = (bot_module.DONATION_CARD, bot_module.DONATION_NAME)
        bot_module.DONATION_CARD, bot_module.DONATION_NAME = card, name
        try:
            return bot_module.donation_text()
        finally:
            bot_module.DONATION_CARD, bot_module.DONATION_NAME = saved

    def test_sixteen_digits_are_grouped_in_fours(self):
        text = self._text("8600123456789012")
        self.assertIn("8600 1234 5678 9012", text)

    def test_spaces_and_dashes_in_the_variable_are_tolerated(self):
        for written in ("8600 1234 5678 9012", "8600-1234-5678-9012"):
            self.assertIn("8600 1234 5678 9012", self._text(written))

    def test_holder_name_is_included_when_set(self):
        self.assertIn("Al-Kokandiy", self._text("8600123456789012", "Al-Kokandiy"))

    def test_unset_card_does_not_apologise_for_the_bot(self):
        text = self._text("")
        self.assertIn("bepul", text)
        self.assertNotIn("8600", text)

    def test_wrong_length_is_treated_as_unset(self):
        # A typo in the Railway variable must not publish a broken number.
        for junk in ("8600123456789", "860012345678901234", "card", "0000"):
            self.assertNotIn("<code>", self._text(junk), junk)

    def test_no_card_number_is_hardcoded_anywhere(self):
        import pathlib

        root = pathlib.Path(__file__).resolve().parent.parent
        import re

        for path in (root / "bot.py", root / "docs" / "index.html"):
            found = re.findall(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b", path.read_text())
            self.assertEqual(found, [], f"{path.name} contains something card-shaped")


@unittest.skipIf(bot_module is None, "aiogram not installed")
class TestBotSpeaksTheNewAlphabet(unittest.TestCase):
    """The bot's own prose must be a fixed point of its own converter.

    A tool for the new alphabet writing "tinish" or "yuborish" in its own
    replies is the one typo it cannot afford, and it slipped through twice.
    """

    def _prose_lines(self, text):
        import re

        for line in text.splitlines():
            # The mapping tables deliberately show the old forms on the left.
            if "→" in line:
                continue
            stripped = re.sub(r"<[^>]+>", " ", line)
            if stripped.strip():
                yield stripped

    def test_every_reply_is_already_converted(self):
        from yoz import convert

        texts = {
            "START_TEXT": bot_module.START_TEXT,
            "HELP_TEXT": bot_module.HELP_TEXT,
            "donation (unset)": bot_module.donation_text(),
        }
        for row in bot_module.start_keyboard().inline_keyboard:
            for button in row:
                texts[f"button {button.text!r}"] = button.text
        for command in bot_module.COMMANDS:
            texts[f"/{command.command}"] = command.description

        for where, text in texts.items():
            for line in self._prose_lines(text):
                self.assertEqual(convert(line), line, f"old orthography in {where}: {line!r}")


@unittest.skipIf(bot_module is None, "aiogram not installed")
class TestCommandMenu(unittest.TestCase):
    """The "/" menu is set from COMMANDS at startup, so it cannot drift from
    the handlers — as long as every entry in it is actually handled."""

    def _handled(self):
        from aiogram.filters import Command

        names = set()
        for handler in bot_module.dp.message.handlers:
            for f in handler.filters or []:
                obj = getattr(f, "callback", f)
                if isinstance(obj, Command):
                    names |= {str(c) for c in obj.commands}
        return names

    def test_every_menu_command_has_a_handler(self):
        handled = self._handled()
        for command in bot_module.COMMANDS:
            self.assertIn(command.command, handled, f"/{command.command} is in the menu with no handler")

    def test_names_are_valid_for_telegram(self):
        import re

        for command in bot_module.COMMANDS:
            self.assertRegex(command.command, r"^[a-z0-9_]{1,32}$")
            self.assertTrue(command.description.strip())
            self.assertLessEqual(len(command.description), 256)

    def test_aliases_stay_out_of_the_menu(self):
        # /help and /donat work, but listing them would show the same thing twice.
        listed = {c.command for c in bot_module.COMMANDS}
        self.assertTrue({"help", "donat"}.isdisjoint(listed))
        self.assertTrue({"help", "donat"} <= self._handled())
