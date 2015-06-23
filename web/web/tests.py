from itertools import chain
from django.test import Client, TestCase
from django.core.urlresolvers import reverse
from users.models import User
from problems.models import Problem
from courses.models import ProblemSet, Course


# Create your tests here.
class BasicViewsTestCase(TestCase):
    fixtures = []

    def setUp(self):
        self.user = User.objects.create_user(
            username='gregor',
            email='gregor@jerse.info',
            password='gregor')

        self.course = Course.objects.create()
        prob_set = ProblemSet.objects.create(course=self.course)
        self.problem = Problem.objects.create(problem_set=prob_set)
        self.views = {
            'public':
                [
                    ('login', dict()),
                ],
            'authenticated':
                [
                    ('homepage', dict())
                ],
            'student':
                [
                    ('problem_set_detail', {'problem_set_pk': 1}),
                    ('problem_set_attempts', {'problem_set_pk': 1}),
                    ('course_detail', {'course_pk': 1}),
                    ('problem_solution', {'problem_pk': 1}),
                    ('problem_attempt_file', {'problem_pk': 1}),
                ],
            'teacher':
                [
                    ('problem_edit_file', {'problem_pk': 1}),
                ],
            'teacher_redirect':
                [
                    ('problem_set_move', {'problem_set_pk': 1, 'shift': 1}),
                    ('problem_move', {'problem_pk': 1, 'shift': 1}),
                    ('problem_set_move', {'problem_set_pk': 1, 'shift': 1}),
                    ('problem_move', {'problem_pk': 1, 'shift': 1}),
                ],
        }
        self.default_redirect_view_name = 'login'
        self.client = Client()

    def login(self):
        self.assertTrue(self.client.login(username='gregor', password='gregor'), "Login failed")

    def logout(self):
        self.client.logout()

    def assertCode(self, view, response, code):
        message = "{2}: expected {1}, got {0}.".format(response.status_code, code, view)
        if response.status_code == 302:
            message = message[:-1] + ' (redirects to {0}).'.format(response.url)
        self.assertEqual(response.status_code, code, message)

    def assertRedirect(self, view, kwargs, redirect_view_name=None):
        url = reverse(view, kwargs=kwargs)
        response = self.client.get(url)
        self.assertCode(view, response, 302)
        if redirect_view_name is not None:
            self.assertRedirects(response, '{0}?next={1}'.format(reverse(redirect_view_name), url))
        return response

    def assertOK(self, view, kwargs):
            response = self.client.get(reverse(view, kwargs=kwargs))
            self.assertCode(view, response, 200)

    def assertDenied(self, view, kwargs):
            response = self.client.get(reverse(view, kwargs=kwargs))
            self.assertCode(view, response, 403)

    def testUnauthenticated(self):
        """
        Unauthenticated user must be redirected to login page
        except for public pages.
        """
        public_views = [view for view, args in self.views['public']]
        for view, args in chain.from_iterable(self.views.values()):
            if view not in public_views:
                self.assertRedirect(view, args, 'login')
            else:
                self.assertOK(view, args)

    def testPublicAuthenticated(self):
        """
        Authenticated user should receive status 200 on public pages.
        """
        try:
            self.login()
            for view, args in self.views['public'] + self.views['authenticated']:
                self.assertOK(view, args)
        finally:
            self.logout()

    def testPrivateAuthenticated(self):
        """
        Authenticated user should receive 403 (denied) on non-public pages.
        """
        try:
            self.login()
            public_views = [view for view, _ in self.views['public'] + self.views['authenticated']]
            for view, args in chain.from_iterable(self.views.values()):
                if view not in public_views:
                    self.assertDenied(view, args)
        finally:
            self.logout()

    def testStudent(self):
        """
        Student should receive 200 on views allowed to students.
        Students should receive 403 otherwise.
        """
        try:
            self.login()
            denied = self.views['teacher'] + self.views['teacher_redirect']
            for view, args in denied + self.views['student']:
                self.assertDenied(view, args)
            self.course.students.add(self.user)
            for view, args in self.views['student']:
                self.assertOK(view, args)
            for view, args in denied:
                self.assertDenied(view, args)
        finally:
            self.logout()
            self.course.students.remove(self.user)

    def testTeacher(self):
        """
        Teacher should always receive 200 or 303 (redirect).
        """
        try:
            self.login()
            self.course.teachers.add(self.user)
            redirect_views = [view for view, args in self.views['teacher_redirect']]
            for view, args in chain.from_iterable(self.views.values()):
                if view not in redirect_views:
                    print("OK: " + view)
                    self.assertOK(view, args)
                else:
                    print("Redirect: " + view)
                    self.assertRedirect(view, args)
        finally:
            self.logout()
