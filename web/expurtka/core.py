import courses.models as courses
import putka.models as putka


def migrate_institution(institution):
    p_institution = putka.Set()
    print(institution, p_institution)


def migrate_institutions():
    for institution in courses.Institution.objects.all():
        migrate_institution(institution)
