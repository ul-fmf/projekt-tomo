import json
from django.test import TestCase
from rest_framework.test import APIClient
from users.models import User
from models import Attempt, Part
from courses.models import Course, ProblemSet
from problems.models import Problem


# Create your tests here.
class AttemptSubmitTestCase(TestCase):
    fixtures = ['users.json']

    def setUp(self):
        cour = Course.objects.create()
        prob_set = ProblemSet.objects.create(course=cour)
        self.problem = Problem.objects.create(problem_set=prob_set)
        self.part1 = Part(problem=self.problem, secret='["1"]')
        self.part2 = Part(problem=self.problem, secret='["1", "2"]')
        self.part3 = Part(problem=self.problem, secret='["1", "2", "3"]')

        self.part1.save()
        self.part2.save()
        self.part3.save()
        self.attempts_data = [
            {
                "solution": "s1",
                "valid": False,
                "feedback": ["f1", "f2"],
                "secret": [], "part": 1
            },
            {
                "solution": "s2",
                "valid": True,
                "feedback": ["Error"],
                "secret": ["1"],
                "part": 2
            },
            {
                "solution": "",
                "valid": True,
                "feedback": [],
                "secret": ["1", "2", "3"],
                "part": 3
            },
            {
                "solution": "",
                "valid": True,
                "feedback": [],
                "secret": ["1", "4", "3"],
                "part": 3
            }
        ]
        self.user = User.objects.get(username='matija')
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user.auth_token.key)

    def testSimpleSubmit(self):
        self.assertEqual(Attempt.objects.count(), 0, "There should be no attempts in the database")
        response = self.client.post('/api/attempts/submit/',
                                    self.attempts_data,
                                    format='json'
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Attempt.objects.count(), 3, "There should be exactly two attempts"
                                                     " in the database")

    def testSubmitData(self):
        self.assertEqual(Attempt.objects.count(), 0, "There should be no attempts in the database")
        response = self.client.post('/api/attempts/submit/',
                                    [self.attempts_data[0]],
                                    format='json'
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Attempt.objects.count(), 1, "There should be exactly one attempt"
                                                     " in the database")
        attempt = Attempt.objects.get()

        self.assertEqual(attempt.solution, self.attempts_data[0]["solution"],
                         'Saved and received data must be equal')
        self.assertSequenceEqual(json.loads(attempt.feedback), self.attempts_data[0]["feedback"],
                                 'Saved and received data must be equal')
        self.assertEqual(attempt.valid, self.attempts_data[0]["valid"],
                         'Saved and received data must be equal')
        self.assertEqual(attempt.part.id, self.attempts_data[0]["part"],
                         'Saved and received data must be equal')

    def testInvalidSecret(self):
        self.assertEqual(Attempt.objects.count(), 0, "There should be no attempts in the database")
        response = self.client.post('/api/attempts/submit/',
                                    [self.attempts_data[1]],
                                    format='json'
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Attempt.objects.count(), 1, "There should be exactly one attempt"
                                                     " in the database")
        attempt = Attempt.objects.get()
        self.assertTrue(self.attempts_data[1]["valid"], "Attempt data should be true")
        self.assertFalse(attempt.valid, 'Secret is invalid, attempt must be marked as invalid')

    def testValidSecret(self):
        self.assertEqual(Attempt.objects.count(), 0, "There should be no attempts in the database")
        response = self.client.post('/api/attempts/submit/',
                                    [self.attempts_data[2]],
                                    format='json'
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Attempt.objects.count(), 1, "There should be exactly one attempt"
                                                     " in the database")
        attempt = Attempt.objects.get()
        self.assertTrue(self.attempts_data[1]["valid"], "Attempt data should be true")
        self.assertTrue(attempt.valid, 'Attempt must be marked as valid')

    def testChangedSecret(self):
        self.assertEqual(Attempt.objects.count(), 0, "There should be no attempts in the database")
        response = self.client.post('/api/attempts/submit/',
                                    [self.attempts_data[2]],
                                    format='json'
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Attempt.objects.count(), 1, "There should be exactly one attempt"
                                                     " in the database")
        attempt = Attempt.objects.get()
        self.assertTrue(self.attempts_data[1]["valid"], "Attempt data should be true")
        self.assertTrue(attempt.valid, 'Attempt must be marked as valid')
        response = self.client.post('/api/attempts/submit/',
                                    [self.attempts_data[3]],
                                    format='json'
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Attempt.objects.count(), 1, "There should be exactly one attempt"
                                                     " in the database")
        attempt = Attempt.objects.get()
        self.assertTrue(self.attempts_data[1]["valid"], "Attempt data should be true")
        self.assertFalse(attempt.valid, 'Attempt must be marked as valid')
