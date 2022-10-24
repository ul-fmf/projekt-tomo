# -*- coding: utf-8 -*-

from django.db import migrations, models


def transfer_student_enrollment(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Course = apps.get_model("courses", "Course")
    StudentEnrollment = apps.get_model("courses", "StudentEnrollment")
    for course in Course.objects.all():
        for old_student in course.old_students.all():
            enrollment = StudentEnrollment(course=course, user=old_student)
            enrollment.save()


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0008_auto_20160420_1212"),
    ]

    operations = [
        migrations.RunPython(transfer_student_enrollment),
    ]
