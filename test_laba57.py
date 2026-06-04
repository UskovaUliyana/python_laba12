import unittest
from laba57 import check_password


class TestPasswordAnalyzer(unittest.TestCase):
    
    def test_very_short_password(self):
        score, level, color, tips, max_score = check_password("abc")
        self.assertEqual(level, "Слабый")
        self.assertEqual(color, "#e74c3c")
        self.assertTrue(any("Длина" in t for t in tips))

    def test_only_letters_8chars(self):
        score, level, color, tips, max_score = check_password("abcdefgh")
        self.assertGreaterEqual(score, 2)
        self.assertTrue(any("цифр" in t for t in tips))
        self.assertTrue(any("заглавных" in t for t in tips))
        self.assertTrue(any("спецсимволов" in t for t in tips))

    def test_only_numbers_8chars(self):
        score, level, color, tips, max_score = check_password("12345678")
        self.assertGreaterEqual(score, 2)
        self.assertTrue(any("строчных" in t for t in tips))
        self.assertTrue(any("заглавных" in t for t in tips))
        self.assertTrue(any("спецсимволов" in t for t in tips))

    def test_medium_password(self):
        score, level, color, tips, max_score = check_password("abcd1234")
        self.assertGreaterEqual(score, 3)
        self.assertEqual(level, "Средний")
        self.assertEqual(color, "#f39c12")

    def test_good_password(self):
        score, level, color, tips, max_score = check_password("abcd1234!")
        self.assertGreaterEqual(score, 5)
        self.assertTrue(any("заглавных" in t for t in tips))

    def test_strong_password(self):
        score, level, color, tips, max_score = check_password("Abcd1234!@#$")
        self.assertGreaterEqual(score, 12)
        self.assertEqual(level, "Хороший")
        self.assertEqual(color, "#2ecc71")

    def test_missing_uppercase(self):
        score, level, color, tips, max_score = check_password("abcd1234!")
        self.assertTrue(any("заглавных" in t for t in tips))

    def test_missing_lowercase(self):
        score, level, color, tips, max_score = check_password("ABCD1234!")
        self.assertTrue(any("строчных" in t for t in tips))

    def test_missing_digits(self):
        score, level, color, tips, max_score = check_password("AbcdEfgh!")
        self.assertTrue(any("цифр" in t for t in tips))

    def test_missing_special(self):
        score, level, color, tips, max_score = check_password("Abcd12345")
        self.assertTrue(any("спецсимволов" in t for t in tips))

    def test_common_password(self):
        score, level, color, tips, max_score = check_password("123456")
        self.assertTrue(any("распространённый" in t for t in tips))

    def test_sequential_password(self):
        score, level, color, tips, max_score = check_password("12345678")
        self.assertTrue(any("последовательность" in t for t in tips))

    def test_repeating_chars(self):
        score, level, color, tips, max_score = check_password("aaaaaaaa")
        self.assertTrue(any("повторяющихся" in t for t in tips))

    def test_date_password(self):
        score, level, color, tips, max_score = check_password("12011990")
        self.assertTrue(any("дату" in t for t in tips))

    def test_repeating_blocks(self):
        score, level, color, tips, max_score = check_password("abcabc123123")
        self.assertTrue(any("повторяющихся" in t for t in tips))

    def test_dict_word_password(self):
        score, level, color, tips, max_score = check_password("admin123")
        self.assertTrue(any("слово" in t for t in tips))

    def test_color_weak(self):
        score, level, color, tips, max_score = check_password("abc")
        self.assertEqual(color, "#e74c3c")

    def test_color_medium(self):
        score, level, color, tips, max_score = check_password("abcd1234")
        self.assertEqual(color, "#f39c12")

    def test_color_good(self):
        score, level, color, tips, max_score = check_password("Abcd1234!")
        self.assertEqual(color, "#f39c12")

    def test_color_strong(self):
        score, level, color, tips, max_score = check_password("Abcd1234!@#$")
        self.assertEqual(color, "#2ecc71")

    def test_bonus_for_diversity(self):
        score1, _, _, _, _ = check_password("aaaaaaaa")
        score2, _, _, _, _ = check_password("aA1!")
        self.assertGreater(score2, score1)

    def test_bonus_for_length(self):
        score1, _, _, _, _ = check_password("aA1!")
        score2, _, _, _, _ = check_password("aA1!aA1!aA1!")
        self.assertGreater(score2, score1)

    def test_max_score_limit(self):
        score, level, color, tips, max_score = check_password("Abcd1234!@#$Qwer")
        self.assertLessEqual(score, max_score)
        self.assertEqual(max_score, 16)

    def test_return_values_count(self):
        result = check_password("test")
        self.assertEqual(len(result), 5)

    def test_length_8_boundary(self):
        score, level, color, tips, max_score = check_password("abcdefgh")
        self.assertGreaterEqual(score, 1)

    def test_length_12_boundary(self):
        score, level, color, tips, max_score = check_password("abcdefghijkl")
        self.assertGreaterEqual(score, 2)

    def test_length_16_boundary(self):
        score, level, color, tips, max_score = check_password("abcdefghijklmnop")
        self.assertGreaterEqual(score, 3)

    def test_length_33_too_long(self):
        score, level, color, tips, max_score = check_password("a" * 33)
        self.assertTrue(any("32" in t for t in tips))


if __name__ == '__main__':
    unittest.main()