import courses.models as tomo


def export_institutions(courses):
    return [
        {
            "pk": institution.pk,
            "title": institution.name,
            "url": institution.name.lower().replace(" ", "_"),
            "public": True,
        }
        for institution in tomo.Institution.objects.filter(
            pk__in=courses.values("institution")
        )
    ]


def export_courses(courses):
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
        for course in courses
    ]


def export_studentenrollments():
    pass


def export_coursegroups():
    pass


def export_problemsets(courses):  # -> list[dict[str, Any]]:
    return [
        {
            "pk": problem_set.pk,
            "parent": problem_set.course.id,
            "title": problem_set.title,
            "description": problem_set.description,
            "public": problem_set.visible,
            "url": problem_set.title.lower().replace(" ", "_"),
            "sort" : problem_set._order,
        }
        for problem_set in tomo.ProblemSet.objects.filter(course__in=courses)
    ]


def export_all(courses):
    institutions = export_institutions(courses)
    exported_courses = export_courses(courses)
    export_studentenrollments()
    export_coursegroups()
    problem_sets = export_problemsets(courses)
    return institutions, exported_courses, problem_sets
