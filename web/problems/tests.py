from courses.models import Course, ProblemSet
from django.test import TestCase
from model_mommy import mommy
from problems.templates.python.check import Check

from .models import Part, Problem


class PartTestCase(TestCase):
    def test_check_secret(self):
        cour = mommy.make("courses.Course")
        prob_set = mommy.make("courses.ProblemSet", course=cour)
        prob = mommy.make("problems.Problem", problem_set=prob_set)

        part0 = mommy.make("problems.Part", problem=prob)
        self.assertEqual(part0.check_secret([]), (True, None))
        self.assertEqual(part0.check_secret(["1"]), (False, None))

        part1 = mommy.make("problems.Part", problem=prob, secret='["1"]')
        self.assertEqual(part1.check_secret([]), (False, None))
        self.assertEqual(part1.check_secret(["1"]), (True, None))
        self.assertEqual(part1.check_secret([1]), (False, 0))
        self.assertEqual(part1.check_secret(["1", "2"]), (False, None))

        part2 = mommy.make("problems.Part", problem=prob, secret='["1", "2"]')
        self.assertEqual(part2.check_secret([]), (False, None))
        self.assertEqual(part2.check_secret(["1"]), (False, None))
        self.assertEqual(part2.check_secret(["1", "2"]), (True, None))
        self.assertEqual(part2.check_secret([1, "2"]), (False, 0))
        self.assertEqual(part2.check_secret(["1", 2]), (False, 1))
        self.assertEqual(part2.check_secret(["1", "2", "3"]), (False, None))


class ApproxTestCase(TestCase):
    def test_basic(self):
        import numpy as np

        a = np.array([1, 2, 3], dtype=float)
        Check.initialize([{"solution": "..."}])
        Check.part()
        self.assertTrue(Check.approx("np.array([1, 2, 3], dtype='float')", a))
        self.assertFalse(Check.approx("[1, 2, 3]", a))
        self.assertEquals(
            Check.current_part["feedback"][-1],
            "Rezultat ima napačen tip. Pričakovan tip: ndarray, dobljen tip: list.",
        )
        self.assertFalse(Check.approx("np.zeros((2, 3))", a))
        self.assertEquals(
            Check.current_part["feedback"][-1],
            "Obliki se ne ujemata. Pričakovana oblika: (3,), dobljena oblika: (2, 3).",
        )
        self.assertFalse(Check.approx("np.array([1, 2, 3.1])", a))
        self.assertRegexpMatches(
            Check.current_part["feedback"][-1], r"Rezultat ni pravilen\..*"
        )
