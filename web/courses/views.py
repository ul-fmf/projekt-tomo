from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Course, ProblemSet
from problems.models import Part
from attempts.models import Attempt
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

    problem_success = []
    for problem in problem_set.problems.all():
        if request.user.can_edit_course(course):
            success = problem.student_success()
        else:
            success = {
                'valid': 0,
                'invalid': 0,
                'nothing': 0
            }
            for part in problem.parts.all():
                if part.pk in valid_parts_ids:
                    success['valid'] += 1
                elif part.pk in invalid_parts_ids:
                    success['invalid'] += 1
                else:
                    success['nothing'] += 1
        problem_success.append((problem, success))

    return render(request, 'courses/problem_set_detail.html', {
        'problem_set': problem_set,
        'problems': problem_set.problems.all(),
        'valid_parts_ids': valid_parts_ids,
        'invalid_parts_ids': invalid_parts_ids,
        'problem_success': problem_success,
        'show_teacher_forms': request.user.can_edit_course(course),
        'user': user,
    })


@login_required
def course_detail(request, course_pk):
    """Show a list of all problems in a problem set."""
    course = get_object_or_404(Course, pk=course_pk)
    verify(request.user.can_view_course(course))
    if request.user.can_edit_course(course):
        students = list(course.students.exclude(taught_courses=course))
        part_count = Part.objects.filter(problem__problem_set__course=course).count()
        attempts = Attempt.objects.filter(part__problem__problem_set__course=course)
        from django.db.models import Count
        valid_attempts = attempts.filter(valid=True).values('user').annotate(Count('user'))
        all_attempts = attempts.values('user').annotate(Count('user'))
        def to_dict(attempts):
            attempts_dict = {}
            for val in attempts:
                attempts_dict[val['user']] = val['user__count']
            return attempts_dict
        valid_attempts_dict = to_dict(valid_attempts)
        all_attempts_dict = to_dict(all_attempts)
        for student in students:
            student.valid = valid_attempts_dict.get(student.pk, 0)
            student.invalid = all_attempts_dict.get(student.pk, 0) - student.valid
            student.empty = part_count - student.valid - student.invalid
    else:
        students = []
    course.annotate_for_user(request.user)
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'students': students,
        'show_teacher_forms': request.user.can_edit_course(course),
    })


@login_required
def course_users(request, course_pk):
    """Show a list of all course students and teachers"""
    course = get_object_or_404(Course, pk=course_pk)
    verify(request.user.can_edit_course(course))
    students = list(course.students.all())
    part_count = Part.objects.filter(problem__problem_set__course=course).count()
    attempts = Attempt.objects.filter(part__problem__problem_set__course=course)
    from django.db.models import Count
    valid_attempts = attempts.filter(valid=True).values('user').annotate(Count('user'))
    all_attempts = attempts.values('user').annotate(Count('user'))
    def to_dict(attempts):
        attempts_dict = {}
        for val in attempts:
            attempts_dict[val['user']] = val['user__count']
        return attempts_dict
    valid_attempts_dict = to_dict(valid_attempts)
    all_attempts_dict = to_dict(all_attempts)
    for student in students:
        student.correct_percentage = "{}%".format(100.0 * valid_attempts_dict.get(student.pk, 0) / part_count)
        student.incorrect_percentage = "{}%".format(100.0 * (all_attempts_dict.get(student.pk, 0) - valid_attempts_dict.get(student.pk, 0)) / part_count)
    return render(request, 'courses/course_users.html', {
        'course': course,
        'students': students
    })


@login_required
def promote_to_teacher(request, course_pk, student_pk):
    """Promote student to teacher in a given course"""
    course = get_object_or_404(Course, pk=course_pk)
    verify(request.user.can_edit_course(course))
    student = get_object_or_404(User, pk=student_pk)
    course.teachers.add(student)
    course.students.remove(student)
    return redirect(course)


@login_required
def demote_to_student(request, course_pk, teacher_pk):
    """Demote teacher to student in a given course"""
    course = get_object_or_404(Course, pk=course_pk)
    verify(request.user.can_edit_course(course))
    teacher = get_object_or_404(User, pk=teacher_pk)
    course.students.add(teacher)
    course.teachers.remove(teacher)
    return redirect(course)


@login_required
def homepage(request):
    """Show a list of all problems in a problem set."""
    user_courses = []
    not_user_courses = []
    for course in Course.objects.all():
        if request.user.is_favourite_course(course):
            user_courses.append(course)
            course.annotate_for_user(request.user)
            course.annotated_problem_sets = course.annotated_problem_sets[-1:-4:-1]
        else:
            not_user_courses.append(course)
    return render(request, 'homepage.html', {
        'user_courses': user_courses,
        'not_user_courses': not_user_courses,
    })


@login_required
def enroll_in_course(request, course_pk):
    """Enrolls user in a course as a student."""
    course = get_object_or_404(Course, pk=course_pk)
    course.students.add(request.user)
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def unenroll_from_course(request, course_pk):
    """Unenrolls user (student or teacher) from a course."""
    course = get_object_or_404(Course, pk=course_pk)
    course.students.remove(request.user)
    course.teachers.remove(request.user)
    return redirect(request.META.get('HTTP_REFERER'))


@require_POST
@login_required
def problem_set_move(request, problem_set_pk):
    problem_set = get_object_or_404(ProblemSet, pk=problem_set_pk)
    verify(request.user.can_edit_course(problem_set.course))
    print request.POST
    if 'move_up' in request.POST:
        problem_set.move(-1)
    elif 'move_down' in request.POST:
        problem_set.move(1)
    return redirect(problem_set.course)


class ProblemSetCreate(CreateView):
    model = ProblemSet
    fields = ['title', 'description', 'visible', 'solution_visibility']

    def get_context_data(self, **kwargs):
        context = super(ProblemSetCreate, self).get_context_data(**kwargs)
        context['course_pk'] = self.kwargs['course_pk']
        return context

    def form_valid(self, form):
        course = get_object_or_404(Course, id=self.kwargs['course_pk'])
        verify(self.request.user.can_edit_course(course))
        form.instance.course = course
        return super(ProblemSetCreate, self).form_valid(form)


class ProblemSetUpdate(UpdateView):
    model = ProblemSet
    fields = ['title', 'description']

    def get_object(self, *args, **kwargs):
        obj = super(ProblemSetUpdate, self).get_object(*args, **kwargs)
        verify(self.request.user.can_edit_problem_set(obj))
        return obj


class ProblemSetDelete(DeleteView):
    model = ProblemSet

    def get_object(self, *args, **kwargs):
        obj = super(ProblemSetDelete, self).get_object(*args, **kwargs)
        verify(self.request.user.can_edit_course(obj.course))
        return obj

    def get_success_url(self):
        return self.object.course.get_absolute_url()


@require_POST
@login_required
def problem_set_toggle_visible(request, problem_set_pk):
    problem_set = get_object_or_404(ProblemSet, pk=problem_set_pk)
    verify(request.user.can_edit_problem_set(problem_set))
    problem_set.toggle_visible()
    return redirect(problem_set.course)


@require_POST
@login_required
def problem_set_toggle_solution_visibility(request, problem_set_pk):
    problem_set = get_object_or_404(ProblemSet, pk=problem_set_pk)
    verify(request.user.can_edit_problem_set(problem_set))
    problem_set.toggle_solution_visibility()
    return redirect(problem_set.course)


@login_required
def course_progress(request, course_pk, user_pk):
    course = get_object_or_404(Course, id=course_pk)
    user = get_object_or_404(User, id=user_pk)
    verify(request.user.can_view_course_attempts(course))
    return render(request, "courses/course_progress.html", {
        'course': course,
        'observed_user': user,
        'course_attempts': course.user_attempts(user)
    })
