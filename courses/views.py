from django.shortcuts import get_object_or_404, redirect
from tomo.utils import verify
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
