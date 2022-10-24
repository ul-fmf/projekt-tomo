from itertools import chain

from courses.models import Course, ProblemSet
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from model_mommy import mommy
from problems.models import Problem
from users.models import User


# Create your tests here.
class BasicViewsTestCase(TestCase):
    fixtures = []

    def setUp(self):
        self.user = User.objects.create_user(username="USER", password="PASS")
        self.other_user = mommy.make("users.User")
        self.course = mommy.make("courses.Course")
        prob_set = mommy.make("courses.ProblemSet", course=self.course)
        visible_prob_set = mommy.make(
            "courses.ProblemSet", course=self.course, visible=True
        )
        problem = mommy.make("problems.Problem", problem_set=prob_set)
        visible_problem = mommy.make("problems.Problem", problem_set=visible_prob_set)
        self.views = {
            "public": [
                ("login", dict()),
                ("terms_of_service", dict()),
                ("help", dict()),
                ("help_students", dict()),
                ("help_teachers", dict()),
            ],
            "authenticated": [
                ("homepage", dict()),
                ("problem_set_detail", {"problem_set_pk": visible_prob_set.pk}),
                ("course_detail", {"course_pk": self.course.pk}),
                ("problem_attempt_file", {"problem_pk": visible_problem.pk}),
                ("problem_set_attempts", {"problem_set_pk": visible_prob_set.pk}),
                (
                    "problem_solution",
                    {"problem_pk": visible_problem.pk, "user_pk": self.user.pk},
                ),
            ],
            "student": [],
            "teacher_redirect": [
                ("problem_move", {"problem_pk": problem.pk, "shift": 1}),
                ("problem_move", {"problem_pk": problem.pk, "shift": -1}),
            ],
            "teacher": [
                ("problem_edit_file", {"problem_pk": problem.pk}),
                ("problem_set_edit", {"problem_set_pk": visible_problem.pk}),
                ("problem_set_detail", {"problem_set_pk": prob_set.pk}),
                ("problem_attempt_file", {"problem_pk": problem.pk}),
                ("problem_set_attempts", {"problem_set_pk": prob_set.pk}),
                (
                    "problem_solution",
                    {"problem_pk": problem.pk, "user_pk": self.user.pk},
                ),
                (
                    "problem_solution",
                    {"problem_pk": visible_problem.pk, "user_pk": self.other_user.pk},
                ),
                ("problem_move", {"problem_pk": visible_problem.pk, "shift": 1}),
                ("problem_move", {"problem_pk": visible_problem.pk, "shift": -1}),
                ("problem_set_progress", {"problem_set_pk": prob_set.pk}),
            ],
        }
        self.default_redirect_view_name = "login"
        self.client = Client()

    def login(self):
        self.assertTrue(
            self.client.login(username="USER", password="PASS"), "Login failed"
        )

    def logout(self):
        self.client.logout()

    def assertCode(self, view, response, code):
        message = "{2}: expected {1}, got {0}.".format(response.status_code, code, view)
        if response.status_code == 302:
            message = message[:-1] + " (redirects to {0}).".format(response.url)
        self.assertEqual(response.status_code, code, message)

    def assertRedirect(self, view, kwargs, redirect_view_name=None):
        url = reverse(view, kwargs=kwargs)
        response = self.client.get(url)
        self.assertCode(view, response, 302)
        if redirect_view_name is not None:
            self.assertRedirects(
                response, "{0}?next={1}".format(reverse(redirect_view_name), url)
            )
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
        public_views = [view for view, args in self.views["public"]]
        for view, args in chain.from_iterable(list(self.views.values())):
            if view not in public_views:
                self.assertRedirect(view, args, "login")
            else:
                self.assertOK(view, args)

    def testPublicAuthenticated(self):
        """
        Authenticated user should receive status 200 on public pages.
        """
        try:
            self.login()
            for view, args in self.views["public"] + self.views["authenticated"]:
                self.assertOK(view, args)
        finally:
            self.logout()

    def testPrivateAuthenticated(self):
        """
        Authenticated user should receive 403 (denied) on non-public pages.
        """
        try:
            self.login()
            public_views = [
                view for view, _ in self.views["public"] + self.views["authenticated"]
            ]
            for view, args in chain.from_iterable(list(self.views.values())):
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
            denied = self.views["teacher"] + self.views["teacher_redirect"]
            for view, args in denied + self.views["student"]:
                self.assertDenied(view, args)
            self.course.enroll_student(self.user)
            for view, args in self.views["student"]:
                self.assertOK(view, args)
            for view, args in denied:
                self.assertDenied(view, args)
        finally:
            self.logout()
            self.course.unenroll_student(self.user)

    def testTeacher(self):
        """
        Teacher should always receive 200 or 303 (redirect).
        """
        try:
            self.login()
            self.course.teachers.add(self.user)
            redirect_views = [view for view, args in self.views["teacher_redirect"]]
            for view, args in chain.from_iterable(list(self.views.values())):
                if view not in redirect_views:
                    print(("OK: " + view))
                    self.assertOK(view, args)
                else:
                    print(("Redirect: " + view))
                    self.assertRedirect(view, args)
        finally:
            self.logout()
