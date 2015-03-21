from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from rest_framework.reverse import reverse
from .models import Course, ProblemSet
from utils.views import zip_archive


@login_required
def problem_set_attempts(request, problem_set_pk):
    """Download an archive of attempt files for a given problem set."""
    problem_set = get_object_or_404(ProblemSet, pk=problem_set_pk)
    user = request.user if request.user.is_authenticated() else None
    url = reverse('attempt-submit', request=request)
    archive_name, files = problem_set.attempts_archive(url, user)
    return zip_archive(archive_name, files)


@login_required
def problem_set_detail(request, problem_set_pk):
    """Show a list of all problems in a problem set."""
    problem_set = get_object_or_404(ProblemSet, pk=problem_set_pk)
    user_attempts = request.user.attempts.all()
    valid_parts_ids = user_attempts.filter(valid=True).values_list('part_id', flat=True)
    invalid_parts_ids = user_attempts.filter(valid=False).values_list('part_id', flat=True)
    problems = problem_set.problems.all()
    invalid_problems_ids = problems.filter(parts__id__in=invalid_parts_ids).values_list('id', flat=True)    
    valid_problems_ids = [p.id for p in problems
                          if p.parts.filter(id__in=valid_parts_ids).count() == p.parts.count() and p.parts.count() > 0]
    half_valid_problems_ids = problems.filter(parts__id__in=valid_parts_ids).exclude(id__in=valid_problems_ids).values_list('id', flat=True)

    return render(request, 'courses/problem_set_detail.html', {
        'problem_set': problem_set,
        'problems': problems,
        'valid_parts_ids': valid_parts_ids,
        'invalid_parts_ids': invalid_parts_ids,
        'valid_problems_ids': valid_problems_ids,
        'invalid_problems_ids': invalid_problems_ids,
        'half_valid_problems_ids': half_valid_problems_ids,
    })


@login_required
def course_detail(request, course_pk):
    """Show a list of all problems in a problem set."""
    course = get_object_or_404(Course, pk=course_pk)
    return render(request, 'courses/course_detail.html', {
        'course': course
    })


@login_required
def homepage(request):
    """Show a list of all problems in a problem set."""
    courses = Course.objects.all()
    return render(request, 'homepage.html', {
        'courses': courses
    })
