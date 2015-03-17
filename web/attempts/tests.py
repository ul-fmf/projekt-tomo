import json
from django.test import TestCase
from rest_framework.test import APIClient
from users.models import User
from models import Attempt


# Create your tests here.
class AttemptSubmitTestCase(TestCase):
    fixtures = ['users.json', 'problems.json']

    def setUp(self):
        self.part_data = [
            {
                "solution": "\ndef linearna(a, b):\\n    return -b / a\\n",
                "valid": False,
                "feedback": ["prvi", "drugi feedbk"],
                "secret": [], "part": 1
            },
            {
                "solution": "\\nimport math\\n\\ndef ploscina(n, a):\\n"
                            "return 0.25  a**2  n / math.tan(math.pi / n)",
                "valid": True,
                "feedback": ["Error"],
                "secret": ["12", "13", "14"],
                "part": 2
            },
            {
                "solution": "\\nimport math\\n\\ndef ploscina(n, a):\\n"
                            "return 0.25  a**2  n / math.tan(math.pi / n)",
                "valid": True,
                "feedback": [],
                "secret": ["50.0", "50.0", "50.003431", "50.016074", "50.039984", "50.076335",
                           "50.125903", "50.189237", "50.26674", "50.358713", "50.465379",
                           "50.586898", "50.723383", "38.174018", "38.39575", "38.636906",
                           "38.897301", "37.229021", "37.141819", "37.075118", "37.029275",
                           "37.004586", "37.001295", "37.01959", "37.059605", "37.121422",
                           "24.314968", "24.476049", "24.669555", "24.8949", "25.151384",
                           "25.438211", "25.754502", "26.09931", "24.698178", "24.498323",
                           "24.33105", "24.197178", "24.0974", "11.070231", "11.004787",
                           "11.016182", "11.10442", "11.267924", "11.503695", "11.807604",
                           "12.174731", "12.599721", "13.077091", "13.601471", "14.167774",
                           "13.114877", "6.525166", "5.646199", "4.786354", "3.958587",
                           "3.18855", "2.530215", "2.092648", "2.025258", "2.360635",
                           "2.965638", "3.711041", "4.528345", "5.385165", "16.132476",
                           "16.500874", "16.913566", "17.117243", "16.684926", "16.295202",
                           "15.951273", "15.656237", "15.41298", "15.224063", "15.091602",
                           "15.017165", "15.001688", "28.024361", "28.079525", "28.166247",
                           "28.284271", "28.433241", "28.612707", "28.82213", "29.478806",
                           "29.196794", "28.942883", "28.717852", "28.522415", "28.357215",
                           "41.152488", "41.08183", "41.032933", "41.005896", "41.000782",
                           "41.017617", "41.056393", "41.117066", "41.199557"],
                "part": 3
            }
        ]
        self.user = User.objects.get(username='matija')
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user.auth_token.key)

    def testSimpleSubmit(self):
        self.assertEqual(Attempt.objects.count(), 0, "There should be no attempts in the database")
        response = self.client.post('/api/attempts/submit/',
                                    self.part_data[0:2],
                                    format='json'
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Attempt.objects.count(), 2, "There should be exactly two attempts"
                                                     " in the database")

    def testSubmitData(self):
        self.assertEqual(Attempt.objects.count(), 0, "There should be no attempts in the database")
        response = self.client.post('/api/attempts/submit/',
                                    self.part_data[0:1],
                                    format='json'
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Attempt.objects.count(), 1, "There should be exactly one attempt"
                                                     " in the database")
        attempt = Attempt.objects.get()

        self.assertEqual(attempt.solution, self.part_data[0]["solution"],
                         'Saved and received data must be equal')
        self.assertSequenceEqual(json.loads(attempt.feedback), self.part_data[0]["feedback"],
                                 'Saved and received data must be equal')
        self.assertEqual(attempt.valid, self.part_data[0]["valid"],
                         'Saved and received data must be equal')
        self.assertEqual(attempt.part.id, self.part_data[0]["part"],
                         'Saved and received data must be equal')

    def testInvalidSecret(self):
        self.assertEqual(Attempt.objects.count(), 0, "There should be no attempts in the database")
        response = self.client.post('/api/attempts/submit/',
                                    self.part_data[1:2],
                                    format='json'
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Attempt.objects.count(), 1, "There should be exactly one attempt"
                                                     " in the database")
        attempt = Attempt.objects.get()
        self.assertTrue(self.part_data[1]["valid"], "Attempt date should have valid set to true")
        self.assertFalse(attempt.valid, 'Secret is invalid, attempt must be marked as invalid')

    def testValidSecret(self):
        self.assertEqual(Attempt.objects.count(), 0, "There should be no attempts in the database")
        response = self.client.post('/api/attempts/submit/',
                                    self.part_data[2:3],
                                    format='json'
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Attempt.objects.count(), 1, "There should be exactly one attempt"
                                                     " in the database")
        attempt = Attempt.objects.get()
        self.assertTrue(self.part_data[1]["valid"], "Attempt date should have valid set to true")
        self.assertTrue(attempt.valid, 'Attempt must be marked as valid')
