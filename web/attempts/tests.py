from django.test import TestCase
from rest_framework.test import APIClient
from users.models import User


# Create your tests here.
class TokenLoginTestCase(TestCase):
    fixtures = ['users.json']

    def testAttemptSubmit(self):
        user = User.objects.get(username='matija')
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + user.auth_token.key)
        response = client.post('/api/attempts/submit/',
                               [
                                   {
                                       "solution": "\ndef linearna(a, b):\\n    return -b / a\\n",
                                       "valid": True,
                                       "feedback": ["prvi", "drugi feedbk"],
                                       "secret": [], "part": 1
                                   },
                                   {
                                       "solution": "\\nimport math\\n\\ndef ploscina(n, a):\\n"
                                                   "return 0.25  a**2  n / math.tan(math.pi / n)",
                                       "valid": True,
                                       "feedback": [],
                                       "secret": [],
                                       "part": 2
                                   }
                               ],
                               format='json'
                               )
        self.assertEqual(response.status_code, 200)
