from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect
from courses.models import ProblemSet


@staff_member_required
def problemset_move(request, problemset_id, shift):
    problemset = get_object_or_404(ProblemSet, id=problemset_id)
    problemset.move(shift)
    return redirect(request.META.get('HTTP_REFERER', problemset))

@staff_member_required
def problemset_toggle_solution_visibility(request, problemset_id):
    problemset = get_object_or_404(ProblemSet, id=problemset_id)
    problemset.toggle_solution_visibility()
    return redirect(request.META.get('HTTP_REFERER', problemset))

@staff_member_required
def problemset_toggle_visible(request, problemset_id):
    problemset = get_object_or_404(ProblemSet, id=problemset_id)
    problemset.toggle_visible()
    return redirect(request.META.get('HTTP_REFERER', problemset))
