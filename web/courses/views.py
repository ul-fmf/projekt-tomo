from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from users.models import User
from utils import verify
from utils.views import zip_archive

from .models import Course, CourseGroup, ProblemSet


@login_required
def problem_set_attempts(request, problem_set_pk):
    """Download an archive of attempt files for a given problem set."""
    problem_set = get_object_or_404(ProblemSet, pk=problem_set_pk)
    verify(request.user.can_view_problem_set(problem_set))
    archive_name, files = problem_set.attempts_archive(request.user)
    return zip_archive(archive_name, files)


@login_required
def problem_set_progress(request, problem_set_pk):
    problem_set = get_object_or_404(ProblemSet, pk=problem_set_pk)
    verify(request.user.can_view_problem_set_attempts(problem_set))
    return render(
        request,
        "courses/problem_set_progress.html",
        {
            "problem_set": problem_set,
        },
    )


@login_required
def problem_set_progress_groups(request, problem_set_pk, group_pk):
    problem_set = get_object_or_404(ProblemSet, pk=problem_set_pk)
    group = get_object_or_404(CourseGroup, pk=group_pk)
    verify(request.user.can_view_problem_set_attempts(problem_set))
    return render(
        request,
        "courses/problem_set_progress_groups.html",
        {"problem_set": problem_set, "group": group},
    )


@login_required
def problem_set_static(request, problem_set_pk):
    problem_set = get_object_or_404(ProblemSet, pk=problem_set_pk)
    verify(request.user.can_edit_problem_set(problem_set))
    return render(
        request,
        "courses/problem_set_static.html",
        {
            "problem_set": problem_set,
        },
    )


@login_required
def problem_set_izpit(request, problem_set_pk):
    problem_set = get_object_or_404(ProblemSet, pk=problem_set_pk)
    verify(request.user.can_edit_problem_set(problem_set))
    return render(
        request,
        "courses/problem_set_izpit.html",
        {
            "problem_set": problem_set,
        },
    )


@login_required
def problem_set_tex(request, problem_set_pk):
    problem_set = get_object_or_404(ProblemSet, pk=problem_set_pk)
    verify(request.user.can_edit_problem_set(problem_set))
    tex = render_to_string(
        "courses/izpit-latex-template.tex", {"problem_set": problem_set}
    )
    response = HttpResponse()
    response.write(tex)
    response["Content-Type"] = "application/x-tex; charset=utf-8"
    file_name = "izpit{}.tex".format(problem_set.pk)
    response["Content-Disposition"] = "attachment; filename={0}".format(file_name)
    return response


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
    verify(request.user.can_view_problem_set(problem_set))

    user_attempts = request.user.attempts.filter(
        part__problem__problem_set__id=problem_set_pk
    )
    valid_parts_ids = user_attempts.filter(valid=True).values_list("part_id", flat=True)
    invalid_parts_ids = user_attempts.filter(valid=False).values_list(
        "part_id", flat=True
    )

    return render(
        request,
        "courses/problem_set_detail.html",
        {
            "problem_set": problem_set,
            "valid_parts_ids": valid_parts_ids,
            "invalid_parts_ids": invalid_parts_ids,
            "show_teacher_forms": request.user.can_edit_problem_set(problem_set),
            "student_statistics": problem_set.student_statistics(),
        },
    )


@login_required
def course_detail(request, course_pk):
    """Show a list of all problems in a problem set."""
    course = get_object_or_404(Course, pk=course_pk)
    verify(request.user.can_view_course(course))
    if request.user.can_edit_course(course):
        students = course.student_success()
    else:
        students = []

    course.prepare_annotated_problem_sets(request.user)
    course.annotate(request.user)

    return render(
        request,
        "courses/course_detail.html",
        {
            "course": course,
            "students": students,
            "show_teacher_forms": request.user.can_edit_course(course),
        },
    )


@login_required
def promote_to_teacher(request, course_pk, student_pk):
    """Promote student to teacher in a given course"""
    course = get_object_or_404(Course, pk=course_pk)
    verify(request.user.can_edit_course(course))
    student = get_object_or_404(User, pk=student_pk)
    course.promote_to_teacher(student)
    return redirect(course)


@login_required
def toggle_observed(request, course_pk, student_pk):
    """Promote student to teacher in a given course"""
    course = get_object_or_404(Course, pk=course_pk)
    verify(request.user.can_edit_course(course))
    student = get_object_or_404(User, pk=student_pk)
    course.toggle_observed(student)
    return redirect(course)


@login_required
def demote_to_student(request, course_pk, teacher_pk):
    """Demote teacher to student in a given course"""
    course = get_object_or_404(Course, pk=course_pk)
    verify(request.user.can_edit_course(course))
    teacher = get_object_or_404(User, pk=teacher_pk)
    course.demote_to_student(teacher)
    return redirect(course)


@login_required
def homepage(request):
    """Show a list of all problems in a problem set."""
    user_courses = []
    not_user_courses = []
    for course in (
        Course.objects.order_by("institution__name")
        .select_related("institution")
        .prefetch_related("students", "teachers")
    ):
        if request.user.is_favourite_course(course):
            user_courses.append(course)
            course.prepare_annotated_problem_sets(request.user)
            course.annotated_problem_sets = [
                course for course in course.annotated_problem_sets if course.visible
            ][-1:-4:-1]
            course.annotate(request.user)
        else:
            not_user_courses.append(course)
    return render(
        request,
        "homepage.html",
        {
            "user_courses": user_courses,
            "not_user_courses": not_user_courses,
        },
    )


@login_required
def enroll_in_course(request, course_pk):
    """Enrolls user in a course as a student."""
    course = get_object_or_404(Course, pk=course_pk)
    course.enroll_student(request.user)
    return redirect(request.META.get("HTTP_REFERER"))


@login_required
def unenroll_from_course(request, course_pk):
    """Unenrolls user (student or teacher) from a course."""
    course = get_object_or_404(Course, pk=course_pk)
    course.unenroll_student(request.user)
    return redirect(request.META.get("HTTP_REFERER"))


@require_POST
@login_required
def problem_set_move(request, problem_set_pk):
    problem_set = get_object_or_404(ProblemSet, pk=problem_set_pk)
    verify(request.user.can_edit_course(problem_set.course))
    if "move_up" in request.POST:
        problem_set.move(-1)
    elif "move_down" in request.POST:
        problem_set.move(1)
    return redirect(problem_set.course)


class ProblemSetCreate(CreateView):
    model = ProblemSet
    fields = ["title", "description", "visible", "solution_visibility"]

    def get_context_data(self, **kwargs):
        context = super(ProblemSetCreate, self).get_context_data(**kwargs)
        context["course_pk"] = self.kwargs["course_pk"]
        return context

    def form_valid(self, form):
        course = get_object_or_404(Course, id=self.kwargs["course_pk"])
        verify(self.request.user.can_edit_course(course))
        form.instance.course = course
        return super(ProblemSetCreate, self).form_valid(form)


class ProblemSetUpdate(UpdateView):
    model = ProblemSet
    fields = ["title", "description", "visible", "solution_visibility"]

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
    return render(
        request,
        "courses/course_progress.html",
        {
            "course": course,
            "observed_user": user,
            "course_attempts": course.user_attempts(user),
        },
    )


@login_required
def problem_set_results(request, problem_set_pk):
    problem_set = get_object_or_404(ProblemSet, pk=problem_set_pk)
    verify(request.user.can_view_problem_set_attempts(problem_set))
    archive_name, files = problem_set.results_archive(request.user)
    return zip_archive(archive_name, files)


###############################################################################
# Course Groups related views


@login_required
def course_groups(request, course_pk):
    """
    Main course groups view where we are able to see all current groups and their students,
    update and delete existing groups and create new ones.
    """

    course = get_object_or_404(Course, pk=course_pk)
    verify(request.user.can_view_course_groups(course))

    return render(
        request,
        "courses/course_groups.html",
        {
            "course": course,
            "show_teacher_forms": request.user.can_create_course_groups(course),
            # 'student_success' : course.student_success_by_problemset_grouped_by_groups()
        },
    )


class CourseGroupForm(forms.ModelForm):
    class Meta:

        students = forms.ModelMultipleChoiceField(queryset=User.objects.all())

        model = CourseGroup
        fields = ["title", "description", "students"]
        widgets = {"students": forms.CheckboxSelectMultiple()}

    def __init__(self, course_pk=None, *args, **kwargs):
        super(CourseGroupForm, self).__init__(*args, **kwargs)
        # If the course is given, we can filter the students queryset and only show those enrolled in the course
        if course_pk is not None:
            self.fields["students"].queryset = User.objects.filter(
                studentenrollment__course__pk=course_pk,
                studentenrollment__observed=True,
            ).order_by("first_name")


@login_required
def course_groups_create(request, course_pk):
    """
    Create view for groups following Projekt Tomo's design.
    """

    course = get_object_or_404(Course, id=course_pk)
    if request.method == "POST":
        form = CourseGroupForm(course_pk, request.POST)
        if form.is_valid():
            if request.user.can_create_course_groups(course):
                group = form.save(commit=False)
                group.course = get_object_or_404(
                    Course, id=course_pk
                )  # We get the course from the url
                group.save()
                form.save_m2m()  # We need to call this in order to save all the many to many instances (group, member)
                return redirect("course_groups", course_pk=course_pk)
    else:
        form = CourseGroupForm(course_pk)
    return render(
        request, "courses/coursegroup_form.html", {"form": form, "course_pk": course_pk}
    )


@login_required
def course_groups_update(request, group_pk):
    """
    Update view for groups following Projekt Tomo's design.
    """

    group = get_object_or_404(CourseGroup, id=group_pk)
    course = get_object_or_404(Course, id=group.course.pk)

    if request.method == "POST":
        form = CourseGroupForm(course.pk, request.POST, instance=group)
        if form.is_valid():
            if request.user.can_update_course_groups(course):
                group = form.save()
                return redirect("course_groups", course_pk=course.pk)
    else:
        form = CourseGroupForm(course.pk, instance=group)
    return render(
        request, "courses/coursegroup_form.html", {"form": form, "course_pk": course.pk}
    )


@login_required
def course_groups_confirm_delete(request, group_pk):
    """
    This view will serve a modal window to tell the user if he is sure he wants to
    delete this group.
    """

    group = get_object_or_404(CourseGroup, id=group_pk)
    course_pk = group.course.pk
    course = get_object_or_404(Course, id=course_pk)
    verify(request.user.can_delete_course_groups(course))
    return render(
        request, "courses/coursegroup_confirm_delete.html", {"group_pk": group_pk}
    )


@login_required
def course_groups_delete(request, group_pk):
    group = get_object_or_404(CourseGroup, id=group_pk)
    course_pk = group.course.pk
    course = get_object_or_404(Course, id=course_pk)
    verify(request.user.can_delete_course_groups(course))

    group.delete()

    return redirect("course_groups", course_pk=course_pk)
