from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from .models import Course, ProblemSet


class ProblemSetCase(TestCase):
    def setUp(self):
        course = Course.objects.create()
        ProblemSet.objects.create(course=course)
        ProblemSet.objects.create(course=course)
        ProblemSet.objects.create(course=course)
        user = User.objects.create_user('admin', '', 'admin')
        user.is_staff = True
        user.save()

    def test_problemset_move(self):
        course = Course.objects.get(id=1)
        problemset1 = ProblemSet.objects.get(id=1)
        problemset2 = ProblemSet.objects.get(id=2)
        problemset3 = ProblemSet.objects.get(id=3)
        problemset2.move(1)
        problemset3.move(-1)
        self.assertEqual(course.get_problemset_order(), [3, 1, 2])
        problemset2.move(10)
        problemset3.move(-10)
        self.assertEqual(course.get_problemset_order(), [3, 1, 2])
        problemset1.move(-15)
        problemset3.move(40)
        self.assertEqual(course.get_problemset_order(), [1, 2, 3])

    def test_problemset_move_view(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('courses.views.problemset_move', args=[2, 1]))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('courses.views.problemset_move', args=[3, -1]))
        self.assertEqual(response.status_code, 302)
        course = Course.objects.get(id=1)
        self.assertEqual(course.get_problemset_order(), [3, 1, 2])

    def test_problemset_toggle_visible(self):
        problemset = ProblemSet.objects.get(id=1)
        self.assertEqual(problemset.visible, False)
        problemset.toggle_visible()
        self.assertEqual(problemset.visible, True)
        problemset.toggle_visible()
        self.assertEqual(problemset.visible, False)

    def test_problemset_toggle_visible_view(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('courses.views.problemset_toggle_visible', args=[1]))
        self.assertEqual(response.status_code, 302)
        problemset = ProblemSet.objects.get(id=1)
        self.assertEqual(problemset.visible, True)

    def test_problemset_toggle_solution_visibility(self):
        problemset = ProblemSet.objects.get(id=1)
        self.assertEqual(problemset.solution_visibility, 'pogojno')
        problemset.toggle_solution_visibility()
        self.assertEqual(problemset.solution_visibility, 'vidne')
        problemset.toggle_solution_visibility()
        self.assertEqual(problemset.solution_visibility, 'skrite')
        problemset.toggle_solution_visibility()
        self.assertEqual(problemset.solution_visibility, 'pogojno')

    def test_problemset_toggle_solution_visibility_view(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('courses.views.problemset_toggle_solution_visibility', args=[1]))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('courses.views.problemset_toggle_solution_visibility', args=[1]))
        self.assertEqual(response.status_code, 302)
        problemset = ProblemSet.objects.get(id=1)
        self.assertEqual(problemset.solution_visibility, 'skrite')
