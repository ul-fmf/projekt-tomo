from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from rest_framework.reverse import reverse
from .models import Course, ProblemSet
from users.models import User
from utils.views import zip_archive
from utils import verify


@login_required
def problem_set_attempts(request, problem_set_pk):
    """Download an archive of attempt files for a given problem set."""
    problem_set = get_object_or_404(ProblemSet, pk=problem_set_pk)
    verify(request.user.can_view_problem_set(problem_set))
    archive_name, files = problem_set.attempts_archive(request.user)
    return zip_archive(archive_name, files)


@login_required
def problem_set_edit(request, problem_set_pk):
    """Download an archive of edit files for a given problem set."""
    problem_set = get_object_or_404(ProblemSet, pk=problem_set_pk)
    verify(request.user.can_edit_problem_set(problem_set))
    archive_name, files = problem_set.edit_archive(request.user)
    return zip_archive(archive_name, files)


@login_required
def problem_set_detail(request, problem_set_pk):
    """Show a list of all problems in a problem set."""
    problem_set = get_object_or_404(ProblemSet, pk=problem_set_pk)
    course = problem_set.course
    user = request.user if request.user.is_authenticated() else None
    verify(request.user.can_view_problem_set(problem_set))

    user_attempts = request.user.attempts.filter(part__problem__problem_set__id=problem_set_pk)
    valid_parts_ids = user_attempts.filter(valid=True).values_list('part_id', flat=True)
    invalid_parts_ids = user_attempts.filter(valid=False).values_list('part_id', flat=True)

    attempted_problems = problem_set.attempted_problems(request.user)
    valid_problems_ids = [problem.id for problem in problem_set.valid_problems(request.user)]
    invalid_problems_ids = [problem.id for problem in problem_set.invalid_problems(request.user)]

    half_valid_problems_ids = [problem.id for problem in attempted_problems
                               if problem.id not in valid_problems_ids
                               and problem.id not in invalid_problems_ids]

    return render(request, 'courses/problem_set_detail.html', {
        'problem_set': problem_set,
        'problems': problem_set.problems.all(),
        'valid_parts_ids': valid_parts_ids,
        'invalid_parts_ids': invalid_parts_ids,
        'valid_problems_ids': valid_problems_ids,
        'invalid_problems_ids': invalid_problems_ids,
        'half_valid_problems_ids': half_valid_problems_ids,
        'show_teacher_forms': request.user.can_edit_course(course),
        'user': user,
    })


@login_required
def course_detail(request, course_pk):
    """Show a list of all problems in a problem set."""
    course = get_object_or_404(Course, pk=course_pk)
    verify(request.user.can_view_course(course))
    course.annotated_problem_sets = list(course.problem_sets.reverse())
    for problem_set in course.annotated_problem_sets:
        problem_set.percentage = problem_set.valid_percentage(request.user)
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'show_teacher_forms': request.user.can_edit_course(course),
    })


@login_required
def homepage(request):
    """Show a list of all problems in a problem set."""
    courses = Course.objects.all()
    for course in courses:
        course.annotated_problem_sets = list(course.recent_problem_sets())
        for problem_set in course.annotated_problem_sets:
            problem_set.percentage = problem_set.valid_percentage(request.user)
    return render(request, 'homepage.html', {
        'courses': courses,
        'show_teacher_forms': request.user.can_edit_course(course),
    })


@login_required
def problem_set_move(request, problem_set_pk, shift):
    problem_set = get_object_or_404(ProblemSet, pk=problem_set_pk)
    verify(request.user.can_edit_problem_set(problem_set))
    problem_set.move(shift)
    return redirect(problem_set.course)


class ProblemSetCreate(CreateView):
    model = ProblemSet
    fields = ['title', 'description', 'visible', 'solution_visibility']

    def get_context_data(self, **kwargs):
        context = super(ProblemSetCreate, self).get_context_data(**kwargs)
        course = get_object_or_404(Course, id=self.kwargs['course_pk'])
        verify(self.request.user.can_edit_course(course))
        context['course'] = course
        return context

    def form_valid(self, form):
        course = get_object_or_404(Course, id=self.kwargs['course_pk'])
        form.instance.author = self.request.user
        form.instance.course = course
        verify(self.request.user.can_edit_course(course))
        return super(ProblemSetCreate, self).form_valid(form)


class ProblemSetUpdate(UpdateView):
    model = ProblemSet
    fields = ['title', 'description', 'visible', 'solution_visibility']

    def get_success_url(self):
        return self.object.course.get_absolute_url()

    def get_object(self, *args, **kwargs):
        obj = super(ProblemSetUpdate, self).get_object(*args, **kwargs)
        course = obj.course
        verify(self.request.user.can_edit_course(course))
        return obj

    def form_valid(self, form):
        #problem_set = get_object_or_404(Course, id=self.kwargs['problem_set_id'])
        form.instance.author = self.request.user
        #form.instance.problem_set = problem_set
        #verify(self.request.user.can_edit_problem_set(problem_set))
        return super(ProblemSetUpdate, self).form_valid(form)


class ProblemSetDelete(DeleteView):
    model = ProblemSet

    def get_success_url(self):
        return self.object.course.get_absolute_url()

    def get_object(self, *args, **kwargs):
        obj = super(ProblemSetDelete, self).get_object(*args, **kwargs)
        verify(self.request.user.can_edit_course(obj.course))
        return obj

    def get_context_data(self, **kwargs):
        context = super(ProblemSetDelete, self).get_context_data(**kwargs)
        return context


@login_required
def problem_set_toggle_visible(request, problem_set_pk):
    problem_set = get_object_or_404(ProblemSet, pk=problem_set_pk)
    verify(request.user.can_edit_problem_set(problem_set))
    problem_set.toggle_visible()
    return redirect(problem_set.course)


@login_required
def problem_set_toggle_solution_visibility(request, problem_set_pk):
    problem_set = get_object_or_404(ProblemSet, pk=problem_set_pk)
    verify(request.user.can_edit_problem_set(problem_set))
    problem_set.toggle_solution_visibility()
    return redirect(problem_set.course)

@login_required
def problem_set_progress(request, problem_set_pk):
    problem_set = get_object_or_404(ProblemSet, id=problem_set_pk)
    verify(request.user.can_view_problem_set_attempts(problem_set))
    problems = problem_set.problems.all().prefetch_related('parts__attempts__user')
    return render(request, "courses/problem_set_progress.html", {
        'problem_set': problem_set,
        'problems': problems
    })

@login_required
def course_progress(request, course_pk, user_pk):
    course = get_object_or_404(Course, id=course_pk)
    user = get_object_or_404(User, id=user_pk)
    verify(request.user.can_view_course_attempts(course))
    verify(course.is_student(user))
    return render(request, "courses/course_progress.html", {
        'course': course,
        'observed_user': user,
        'course_attempts': course.user_attempts(user)
    })
