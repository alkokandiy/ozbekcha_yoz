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
