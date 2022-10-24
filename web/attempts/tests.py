import json

from django.test import TestCase
from model_bakery import baker
from rest_framework.test import APIClient

from .models import Attempt


class AttemptSubmitTestCase(TestCase):
    def setUp(self):
        course = baker.make("courses.Course")
        problem_set = baker.make("courses.ProblemSet", course=course, visible=True)
        problem = baker.make("problems.Problem", problem_set=problem_set)
        self.part1 = baker.make("problems.Part", problem=problem, secret='["1"]')
        self.part2 = baker.make("problems.Part", problem=problem, secret='["1", "2"]')
        self.part3 = baker.make(
            "problems.Part", problem=problem, secret='["1", "2", "3"]'
        )

        user = baker.make("users.User")
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + user.auth_token.key)

        self.attempts_data = [
            {
                "solution": "s1",
                "valid": False,
                "feedback": ["f1", "f2"],
                "secret": [],
                "part": self.part1.pk,
                "token": self.part1.attempt_token(user),
            },
            {
                "solution": "s2",
                "valid": True,
                "feedback": ["Error"],
                "secret": ["1"],
                "part": self.part2.pk,
                "token": self.part2.attempt_token(user),
            },
            {
                "solution": "",
                "valid": True,
                "feedback": [],
                "secret": ["1", "2", "3"],
                "part": self.part3.pk,
                "token": self.part3.attempt_token(user),
            },
            {
                "solution": "",
                "valid": True,
                "feedback": [],
                "secret": ["1", "4", "3"],
                "part": self.part3.pk,
                "token": self.part3.attempt_token(user),
            },
        ]

    def testSimpleSubmit(self):
        self.assertEqual(
            Attempt.objects.count(), 0, "There should be no attempts in the database"
        )
        response = self.client.post(
            "/api/attempts/submit/", self.attempts_data, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Attempt.objects.count(),
            3,
            "There should be exactly three attempts" " in the database",
        )

    def testSubmitData(self):
        self.assertEqual(
            Attempt.objects.count(), 0, "There should be no attempts in the database"
        )
        response = self.client.post(
            "/api/attempts/submit/", [self.attempts_data[0]], format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Attempt.objects.count(),
            1,
            "There should be exactly one attempt" " in the database",
        )
        attempt = Attempt.objects.get()

        self.assertEqual(
            attempt.solution,
            self.attempts_data[0]["solution"],
            "Saved and received data must be equal",
        )
        self.assertSequenceEqual(
            json.loads(attempt.feedback),
            self.attempts_data[0]["feedback"],
            "Saved and received data must be equal",
        )
        self.assertEqual(
            attempt.valid,
            self.attempts_data[0]["valid"],
            "Saved and received data must be equal",
        )
        self.assertEqual(
            attempt.part.id,
            self.attempts_data[0]["part"],
            "Saved and received data must be equal",
        )

    def testInvalidSecret(self):
        self.assertEqual(
            Attempt.objects.count(), 0, "There should be no attempts in the database"
        )
        response = self.client.post(
            "/api/attempts/submit/", [self.attempts_data[1]], format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Attempt.objects.count(),
            1,
            "There should be exactly one attempt" " in the database",
        )
        attempt = Attempt.objects.get()
        self.assertTrue(self.attempts_data[1]["valid"], "Attempt data should be true")
        self.assertFalse(
            attempt.valid, "Secret is invalid, attempt must be marked as invalid"
        )

    def testValidSecret(self):
        self.assertEqual(
            Attempt.objects.count(), 0, "There should be no attempts in the database"
        )
        response = self.client.post(
            "/api/attempts/submit/", [self.attempts_data[2]], format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Attempt.objects.count(),
            1,
            "There should be exactly one attempt" " in the database",
        )
        attempt = Attempt.objects.get()
        self.assertTrue(self.attempts_data[1]["valid"], "Attempt data should be true")
        self.assertTrue(attempt.valid, "Attempt must be marked as valid")

    def testChangedSecret(self):
        self.assertEqual(
            Attempt.objects.count(), 0, "There should be no attempts in the database"
        )
        response = self.client.post(
            "/api/attempts/submit/", [self.attempts_data[2]], format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Attempt.objects.count(),
            1,
            "There should be exactly one attempt" " in the database",
        )
        attempt = Attempt.objects.get()
        self.assertTrue(self.attempts_data[1]["valid"], "Attempt data should be true")
        self.assertTrue(attempt.valid, "Attempt must be marked as valid")
        response = self.client.post(
            "/api/attempts/submit/", [self.attempts_data[3]], format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Attempt.objects.count(),
            1,
            "There should be exactly one attempt" " in the database",
        )
        attempt = Attempt.objects.get()
        self.assertTrue(self.attempts_data[1]["valid"], "Attempt data should be true")
        self.assertFalse(attempt.valid, "Attempt must be marked as invalid")

    def testHistory(self):
        self.client.post(
            "/api/attempts/submit/", [self.attempts_data[2]], format="json"
        )
        self.client.post(
            "/api/attempts/submit/", [self.attempts_data[3]], format="json"
        )
        self.assertEqual(Attempt.objects.count(), 1)
        attempt = Attempt.objects.get()
        self.assertEqual(attempt.history.count(), 2)
        self.client.post(
            "/api/attempts/submit/", [self.attempts_data[3]], format="json"
        )
        self.assertEqual(attempt.history.count(), 2)
