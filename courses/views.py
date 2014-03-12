from django.shortcuts import get_object_or_404, redirect
from tomo.utils import verify
from .models import ProblemSet


def problemset_move(request, pk, shift):
    problemset = get_object_or_404(ProblemSet, id=pk)
    verify(problemset.course.has_teacher(request.user))
    problemset.move(shift)
    return redirect(request.META.get('HTTP_REFERER', problemset))


def problemset_toggle_visible(request, pk):
    problemset = get_object_or_404(ProblemSet, id=pk)
    verify(problemset.course.has_teacher(request.user))
    problemset.toggle_visible()
    return redirect(request.META.get('HTTP_REFERER', problemset))


def problemset_toggle_solution_visibility(request, pk):
    problemset = get_object_or_404(ProblemSet, id=pk)
    verify(problemset.course.has_teacher(request.user))
    problemset.toggle_solution_visibility()
    return redirect(request.META.get('HTTP_REFERER', problemset))
