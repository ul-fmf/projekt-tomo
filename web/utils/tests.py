from django.core.exceptions import ValidationError
from django.test import TestCase

from . import is_json_string_list, truncate


class IsJSONStringListTestCase(TestCase):
    def test_not_a_json_value(self):
        with self.assertRaisesRegexp(ValidationError, "Not a JSON value."):
            is_json_string_list(["a", "b", "c"])
        with self.assertRaisesRegexp(ValidationError, "Not a JSON value."):
            is_json_string_list(["abc"])
        with self.assertRaisesRegexp(ValidationError, "Not a JSON value."):
            is_json_string_list('["a", "b", "c"')

    def test_not_a_json_list(self):
        with self.assertRaisesRegexp(ValidationError, "Not a JSON list."):
            is_json_string_list("null")
        with self.assertRaisesRegexp(ValidationError, "Not a JSON list."):
            is_json_string_list("1")
        with self.assertRaisesRegexp(ValidationError, "Not a JSON list."):
            is_json_string_list('"a"')
        with self.assertRaisesRegexp(ValidationError, "Not a JSON list."):
            is_json_string_list('{"a": ["b", "c"]}')

    def test_not_a_json_string_list(self):
        with self.assertRaisesRegexp(ValidationError, "Not a JSON list of strings."):
            is_json_string_list("[1, 2, 3]")
        with self.assertRaisesRegexp(ValidationError, "Not a JSON list of strings."):
            is_json_string_list('[1, "2", "3"]')
        with self.assertRaisesRegexp(ValidationError, "Not a JSON list of strings."):
            is_json_string_list('["1", 2, "3"]')
        with self.assertRaisesRegexp(ValidationError, "Not a JSON list of strings."):
            is_json_string_list('["1", "2", 3]')

    def test_json_string_list(self):
        self.assertIsNone(is_json_string_list("[]"))
        self.assertIsNone(is_json_string_list('["1"]'))
        self.assertIsNone(is_json_string_list('["1", "2"]'))
        self.assertIsNone(is_json_string_list('["1", "2", "3"]'))


class TruncateTestCase(TestCase):
    def test_truncate(self):
        self.assertEqual(truncate(50 * "X"), 50 * "X")
        self.assertEqual(truncate(51 * "X"), 47 * "X" + "...")
        self.assertEqual(truncate("Long string"), "Long string")
        self.assertEqual(truncate("Long string", max_length=11), "Long string")
        self.assertEqual(truncate("Long string", max_length=9), "Long s...")
        self.assertEqual(truncate("Long string", max_length=5), "Lo...")
        self.assertEqual(truncate("Long string", max_length=3), "...")
        with self.assertRaisesRegexp(
            ValueError, "Indicator longer than maximum length."
        ):
            self.assertEqual(truncate("Long string", max_length=1), "L...")
        self.assertEqual(truncate("String", max_length=0, indicator=""), "")
        self.assertEqual(truncate("", max_length=0), "")
