import courses.models as tomo
import expurtka.putka as putka


def export_institutions() -> dict[str, putka.Set]:
    institution_map = {}
    for institution in tomo.Institution.objects.all():
        new = putka.Set.objects.create(
            title=institution.name,
            url=institution.name.lower().replace(" ", "_"),
            public=True,
        )
        institution_map[institution.id] = new
    return institution_map


def export_courses(institution_map: dict[str, putka.Set], users_map: dict[str, putka.User]) -> dict[str, putka.Set]:
    course_map = {}
    for course in tomo.Course.objects.all():
        new = putka.Set.objects.create(
            parent=institution_map[course.institution.id],
            title=course.title,
            description=course.description,
            url=course.title.lower().replace(" ", "_"),
        )
        course_map[course.id] = new
        # TODO teachers -> perms
        # TODO export users, institutions first
    return course_map


def export_studentenrollments():
    pass


def export_coursegroups():
    pass


def export_problemsets(course_map: dict[str, putka.Set]) -> dict[str, putka.Set]:
    problemset_map = {}
    for set in tomo.ProblemSet.objects.all():
        new = putka.Set.objects.create(
            parent=course_map[set.course.id],
            title=set.title,
            description=set.description,
            public=set.visible,
            url=set.title.lower().replace(" ", "_"),
        )
        problemset_map[set.id] = new
    return problemset_map


def please(users_map: dict[str, putka.User]):
    institution_map = export_institutions()
    course_map = export_courses(institution_map, users_map)
    export_studentenrollments()
    export_coursegroups()
    problemset_map = export_problemsets(course_map)
    return institution_map, course_map, problemset_map
