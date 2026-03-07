import courses.models as tomo


def export_institutions():
    institution_map = {}
    for institution in tomo.Institution.objects.all():
        institution_map[institution.id] = {
            "title": institution.name,
            "url": institution.name.lower().replace(" ", "_"),
            "public": True,
        }
    return institution_map


def export_courses(institution_map, users_map):
    course_map = {}
    for course in tomo.Course.objects.all():
        course_map[course.id] = {
            "parent": institution_map[course.institution.id],
            "title": course.title,
            "description": course.description,
            "url": course.title.lower().replace(" ", "_"),
        }
        # TODO teachers -> perms
        # TODO export users, institutions first
    return course_map


def export_studentenrollments():
    pass


def export_coursegroups():
    pass


def export_problemsets(course_map):
    problemset_map = {}
    for set in tomo.ProblemSet.objects.all():
        problemset_map[set.id] = {
            "parent": course_map[set.course.id],
            "title": set.title,
            "description": set.description,
            "public": set.visible,
            "url": set.title.lower().replace(" ", "_"),
        }
    return problemset_map


def please(users_map):
    institution_map = export_institutions()
    course_map = export_courses(institution_map, users_map)
    export_studentenrollments()
    export_coursegroups()
    problemset_map = export_problemsets(course_map)
    return institution_map, course_map, problemset_map
