from django.core.exceptions import ValidationError
from django.test import TestCase
from . import is_json_string_list, shorten


class IsJSONStringListTestCase(TestCase):
    def test_not_a_json_value(self):
        with self.assertRaisesRegexp(ValidationError, 'Not a JSON value.'):
            is_json_string_list(['a', 'b', 'c'])
        with self.assertRaisesRegexp(ValidationError, 'Not a JSON value.'):
            is_json_string_list(['abc'])
        with self.assertRaisesRegexp(ValidationError, 'Not a JSON value.'):
            is_json_string_list('["a", "b", "c"')

    def test_not_a_json_list(self):
        with self.assertRaisesRegexp(ValidationError, 'Not a JSON list.'):
            is_json_string_list("null")
        with self.assertRaisesRegexp(ValidationError, 'Not a JSON list.'):
            is_json_string_list("1")
        with self.assertRaisesRegexp(ValidationError, 'Not a JSON list.'):
            is_json_string_list('"a"')
        with self.assertRaisesRegexp(ValidationError, 'Not a JSON list.'):
            is_json_string_list('{"a": ["b", "c"]}')

    def test_not_a_json_string_list(self):
        with self.assertRaisesRegexp(ValidationError, 'Not a JSON list of strings.'):
            is_json_string_list("[1, 2, 3]")
        with self.assertRaisesRegexp(ValidationError, 'Not a JSON list of strings.'):
            is_json_string_list('[1, "2", "3"]')
        with self.assertRaisesRegexp(ValidationError, 'Not a JSON list of strings.'):
            is_json_string_list('["1", 2, "3"]')
        with self.assertRaisesRegexp(ValidationError, 'Not a JSON list of strings.'):
            is_json_string_list('["1", "2", 3]')

    def test_json_string_list(self):
        self.assertIsNone(is_json_string_list("[]"))
        self.assertIsNone(is_json_string_list('["1"]'))
        self.assertIsNone(is_json_string_list('["1", "2"]'))
        self.assertIsNone(is_json_string_list('["1", "2", "3"]'))


class ShortenTestCase(TestCase):
    def test_shorten(self):
        self.assertEqual(shorten(50 * "X"), 50 * "X")
        self.assertEqual(shorten(51 * "X"), 50 * "X" + "...")
        self.assertEqual(shorten("Long string"), "Long string")
        self.assertEqual(shorten("Long string", max_length=11), "Long string")
        self.assertEqual(shorten("Long string", max_length=9), "Long stri...")
        self.assertEqual(shorten("Long string", max_length=5), "Long ...")
        self.assertEqual(shorten("Long string", max_length=1), "L...")
        self.assertEqual(shorten("", max_length=0), "")
