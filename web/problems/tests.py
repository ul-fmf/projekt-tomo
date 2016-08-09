from django.test import TestCase
from courses.models import Course, ProblemSet
from .models import ProblemContents, Part


class PartTestCase(TestCase):
    def test_check_secret(self):
        cour = Course.objects.create()
        prob_set = ProblemSet.objects.create(course=cour)
        prob = ProblemContents.objects.create(problem_set=prob_set)

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
