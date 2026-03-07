import courses.models as tomo


def export_institutions():
    return [
        {
            "pk": institution.pk,
            "title": institution.name,
            "url": institution.name.lower().replace(" ", "_"),
            "public": True,
        }
        for institution in tomo.Institution.objects.all()
    ]


def export_courses():
    return [
        {
            "pk": course.pk,
            "parent": course.institution.id,
            "title": course.title,
            "description": course.description,
            "url": course.title.lower().replace(" ", "_"),
            # TODO teachers -> perms
            # TODO export users, institutions first
        }
        for course in tomo.Course.objects.all()
    ]


def export_studentenrollments():
    pass


def export_coursegroups():
    pass


def export_problemsets():  # -> list[dict[str, Any]]:
    return [
        {
            "pk": problem_set.pk,
            "parent": problem_set.course.id,
            "title": problem_set.title,
            "description": problem_set.description,
            "public": problem_set.visible,
            "url": problem_set.title.lower().replace(" ", "_"),
        }
        for problem_set in tomo.ProblemSet.objects.all()
    ]


def export_all():
    institutions = export_institutions()
    courses = export_courses()
    export_studentenrollments()
    export_coursegroups()
    problem_sets = export_problemsets()
    return institutions, courses, problem_sets
