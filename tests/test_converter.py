"""Stdlib-only tests: ``python -m unittest discover -s tests``."""

import unittest

from yoz import convert


class TestPrimaryExample(unittest.TestCase):
    def test_spec_example(self):
        self.assertEqual(
            convert("O'zbekiston - sharafli va chiroyli yurt, g'alaba bizniki!"),
            "Özbekiston - şarafli va çiroyli yurt, ğalaba bizniki!",
        )


class TestCase(unittest.TestCase):
    def test_sh_case_variants(self):
        self.assertEqual(convert("SHARAF"), "ŞARAF")
        self.assertEqual(convert("Sharaf"), "Şaraf")
        self.assertEqual(convert("sharaf"), "şaraf")

    def test_ch_case_variants(self):
        self.assertEqual(convert("CHOY"), "ÇOY")
        self.assertEqual(convert("Choy"), "Çoy")
        self.assertEqual(convert("choy"), "çoy")

    def test_mixed_case_digraph_follows_first_letter(self):
        self.assertEqual(convert("sHaraf"), "şaraf")
        self.assertEqual(convert("ShARAF"), "ŞARAF")

    def test_o_and_g_case(self):
        self.assertEqual(convert("O'ZBEK o'zbek G'OZ g'oz"), "ÖZBEK özbek ĞOZ ğoz")


class TestApostropheVariants(unittest.TestCase):
    def test_all_variants_equal(self):
        for apostrophe in "'’‘`ʻʼ´′":
            self.assertEqual(convert("o" + apostrophe + "zbek"), "özbek")
            self.assertEqual(convert("G" + apostrophe + "ijduvon"), "Ğijduvon")

    def test_apostrophe_not_after_o_or_g_is_kept(self):
        self.assertEqual(convert("san'at"), "san'at")
        self.assertEqual(convert("in'om"), "in'om"),
        self.assertEqual(convert("qal'a"), "qal'a")

    def test_separator_apostrophe_blocks_false_digraph(self):
        # The apostrophe keeps s+h apart, so it must not become "ş".
        self.assertEqual(convert("is'hoq"), "is'hoq")
        self.assertEqual(convert("as'hob"), "as'hob")


class TestPreservation(unittest.TestCase):
    def test_structure_is_untouched(self):
        src = "1. Shart\n\n2. *Chiroq*  — yoqildi \U0001f389\n   - o'n\ttab\n"
        self.assertEqual(
            convert(src),
            "1. Şart\n\n2. *Çiroq*  — yoqildi \U0001f389\n   - ön\ttab\n",
        )

    def test_code_block_fences_survive(self):
        src = "```\nprint('choy')\n```"
        self.assertEqual(convert(src), "```\nprint('çoy')\n```")

    def test_other_letters_untouched(self):
        self.assertEqual(convert("qwertyuiopasdfghjklzxcvbnm"), "qwertyuiopasdfghjklzxcvbnm")

    def test_cyrillic_untouched(self):
        self.assertEqual(convert("Шараф ва чирой"), "Шараф ва чирой")

    def test_already_converted_text_is_stable(self):
        once = convert("O'zbekiston shahri")
        self.assertEqual(convert(once), once)
        self.assertEqual(once, "Özbekiston şahri")

    def test_empty_and_whitespace(self):
        self.assertEqual(convert(""), "")
        self.assertEqual(convert("   \n  "), "   \n  ")


class TestNoCascading(unittest.TestCase):
    def test_single_pass_does_not_rescan_output(self):
        # "s" + "ch" must not be read as "sh" after "c" disappears.
        self.assertEqual(convert("ischi"), "isçi")
        self.assertEqual(convert("boshcha"), "boşça")

    def test_adjacent_digraphs(self):
        self.assertEqual(convert("shch"), "şç")
        self.assertEqual(convert("o'g'il"), "öğil")

    def test_trailing_o_with_no_apostrophe(self):
        self.assertEqual(convert("o"), "o")
        self.assertEqual(convert("g"), "g")
        self.assertEqual(convert("s"), "s")


class TestRealWords(unittest.TestCase):
    def test_sentence(self):
        self.assertEqual(
            convert("Toshkent shahrida choyxona bor, g'isht devor, O'rtacha narx."),
            "Toşkent şahrida çoyxona bor, ğişt devor, Örtaça narx.",
        )

    def test_long_text_length_never_grows(self):
        src = "O'zbekiston " * 500
        self.assertLessEqual(len(convert(src)), len(src))


if __name__ == "__main__":
    unittest.main()
