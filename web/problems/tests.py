from django.test import TestCase
from .models import Problem, Part


class PartTestCase(TestCase):
    def test_check_secret(self):
        prob = Problem.objects.create()

        part0 = Part.objects.create(problem=prob)
        self.assertEqual(part0.check_secret([]), (True, None))
        self.assertEqual(part0.check_secret(["1"]), (False, None))

        part1 = Part.objects.create(problem=prob, secret='["1"]')
        self.assertEqual(part1.check_secret([]), (False, None))
        self.assertEqual(part1.check_secret(["1"]), (True, None))
        self.assertEqual(part1.check_secret([1]), (False, 0))
        self.assertEqual(part1.check_secret(["1", "2"]), (False, None))

        part2 = Part.objects.create(problem=prob, secret='["1", "2"]')
        self.assertEqual(part2.check_secret([]), (False, None))
        self.assertEqual(part2.check_secret(["1"]), (False, None))
        self.assertEqual(part2.check_secret(["1", "2"]), (True, None))
        self.assertEqual(part2.check_secret([1, "2"]), (False, 0))
        self.assertEqual(part2.check_secret(["1", 2]), (False, 1))
        self.assertEqual(part2.check_secret(["1", "2", "3"]), (False, None))
