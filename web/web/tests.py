from django.test import Client, TestCase
from django.core.urlresolvers import reverse


# Create your tests here.
class BasicViewsTestCase(TestCase):
    fixtures = []

    def setUp(self):
        self.public_views = [('login', dict()), ('logout', dict())]
        self.private_views = [('homepage', dict()),
                              ('problem_set_detail', {'problem_set_pk': 1}),
                              ('problem_set_attempts', {'problem_set_pk': 1}),
                              ('problem_set_move', {'problem_set_pk': 1, 'shift': 1}),
                              ('course_detail', {'course_pk': 1}),
                              ('problem_solution', {'problem_pk': 1}),
                              ('problem_attempt_file', {'problem_pk': 1}),
                              ('problem_edit_file', {'problem_pk': 1}),
                              ('problem_move', {'problem_pk': 1, 'shift': 1}),
                              ]
        self.client = Client()

    def testPublicUnauthenticated(self):
        for view, args in self.public_views:
            response = self.client.get(reverse(view, kwargs=args))
            self.assertEqual(response.status_code, 200,
                             "Status code {0} instead of 200".format(response.status_code))

    def testPrivateUnauthenticated(self):
        for view, args in self.private_views:
            response = self.client.get(reverse(view, kwargs=args))
            self.assertEqual(response.status_code, 302,
                             "Status code {0} instead of 302".format(response.status_code))
