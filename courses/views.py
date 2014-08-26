from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import FormView
from tomo.utils import verify
from .forms import CoursesForm
from .models import ProblemSet


def problemset_move(request, problemset_id, shift):
    problemset = get_object_or_404(ProblemSet, id=problemset_id)
    verify(problemset.course.has_teacher(request.user))
    problemset.move(shift)
    return redirect(request.META.get('HTTP_REFERER', problemset))


def problemset_toggle_visible(request, problemset_id):
    problemset = get_object_or_404(ProblemSet, id=problemset_id)
    verify(problemset.course.has_teacher(request.user))
    problemset.toggle_visible()
    return redirect(request.META.get('HTTP_REFERER', problemset))


def problemset_toggle_solution_visibility(request, problemset_id):
    problemset = get_object_or_404(ProblemSet, id=problemset_id)
    verify(problemset.course.has_teacher(request.user))
    problemset.toggle_solution_visibility()
    return redirect(request.META.get('HTTP_REFERER', problemset))


class SelectCoursesView(FormView):
    form_class = CoursesForm
    template_name = 'modal/settings.html'
    success_url = reverse_lazy('homepage')

    def get_initial(self):
        super(SelectCoursesView, self).get_initial()
        self.initial = {'courses': self.request.user.courses.all()}
        return self.initial

    def form_valid(self, form):
        form.update_courses(self.request.user)
        return super(SelectCoursesView, self).form_valid(form)