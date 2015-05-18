from django.test import Client, TestCase
from django.core.urlresolvers import reverse
from users.models import User
from problems.models import Problem
from courses.models import ProblemSet, Course


# Create your tests here.
class BasicViewsTestCase(TestCase):
    fixtures = ['users.json']

    def setUp(self):
        self.user = User.objects.get(username='gregor')
        self.course = Course.objects.create()
        prob_set = ProblemSet.objects.create(course=self.course)
        self.problem = Problem.objects.create(problem_set=prob_set)

        self.public_views = [('login', dict()), ('logout', dict())]
        self.authenticated_private_views = [
            ('homepage', dict()),
            ]
        self.student_private_views = [
            ('problem_set_detail', {'problem_set_pk': 1}),
            ('problem_set_attempts', {'problem_set_pk': 1}),
            ('course_detail', {'course_pk': 1}),
            ('problem_solution', {'problem_pk': 1}),
            ('problem_attempt_file', {'problem_pk': 1}),
            ]
        self.teacher_private_views = [
            ('problem_edit_file', {'problem_pk': 1}),
            ]
        self.teacher_redirect_views = [
            ('problem_set_move', {'problem_set_pk': 1, 'shift': 1}),
            ('problem_move', {'problem_pk': 1, 'shift': 1}),
            ('problem_set_move', {'problem_set_pk': 1, 'shift': 1}),
            ('problem_move', {'problem_pk': 1, 'shift': 1}),
        ]
        self.default_redirect_view_name = 'login'
        self.redirect_view_name = {
            'problem_move': 'admin:login',
            'problem_set_move': 'admin:login'}
        self.client = Client()

    def assertCode(self, view, response, code):
        message = "{2}: expected {1}, got {0}.".format(response.status_code, code, view)
        if response.status_code == 302:
            message = message[:-1] + ' (redirects to {0}).'.format(response.url)
        self.assertEqual(response.status_code, code, message)

    def assertRedirect(self, client, view, kwargs, redirected_view=None):
        url = reverse(view, kwargs=kwargs)
        response = self.client.get(url)
        self.assertCode(view, response, 302)
        if redirected_view is not None:
            redirect_view_name = self.redirect_view_name.get(view, redirected_view)
            self.assertRedirects(response, '{0}?next={1}'.format(reverse(redirect_view_name), url))
        return response

    def assertOK(self, client, view, kwargs):
            response = self.client.get(reverse(view, kwargs=kwargs))
            self.assertCode(view, response, 200)

    def assertDenied(self, client, view, kwargs):
            response = self.client.get(reverse(view, kwargs=kwargs))
            self.assertCode(view, response, 403)

    def testLoginRedirect(self):
        response = self.client.get('/')
        self.assertRedirects(response, '{0}{1}'.format(reverse('login'), '?next=/'))

    def testPublicUnauthenticated(self):
        for view, args in self.public_views:
            self.assertOK(self.client, view, args)

    def testPrivateUnauthenticated(self):
        for view, args in self.teacher_private_views + self.student_private_views:
            redirect_view_name = self.redirect_view_name.get(view, self.default_redirect_view_name)
            self.assertRedirect(self.client, view, args, redirect_view_name)

    def testPublicAuthenticated(self):
        self.client.login(username='gregor', password='gregor')
        for view, args in self.public_views:
            self.assertOK(self.client, view, args)
        self.client.logout()

    def testPrivateAuthenticated(self):
        self.client.login(username='gregor', password='gregor')
        for view, args in self.authenticated_private_views:
            self.assertOK(self.client, view, args)
        for view, args in self.student_private_views:
            self.assertRedirect(self.client, view, args, 'login')
        for view, args in self.teacher_private_views:
            self.assertRedirect(self.client, view, args, 'login')

    def testStudentAuthenticated(self):
        self.course.students.add(self.user)
        self.client.login(username='gregor', password='gregor')
        for view, args in self.authenticated_private_views + self.student_private_views:
            self.assertOK(self.client, view, args)
        for view, args in self.teacher_private_views + self.teacher_redirect_views:
            self.assertDenied(self.client, view, args)
        self.client.logout()
        self.course.students.remove(self.user)

    def testTeacherAuthenticated(self):
        self.course.teachers.add(self.user)
        self.client.login(username='gregor', password='gregor')
        views = (self.authenticated_private_views +
                 self.student_private_views +
                 self.teacher_private_views)
        for view, args in views:
            self.assertOK(self.client, view, args)
        for view, args in self.teacher_redirect_views:
            self.assertRedirect(self.client, view, args)
        self.client.logout()
        self.course.students.remove(self.user)
