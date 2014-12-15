# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def add_default_languages(apps, schema_editor):
    Language = apps.get_model("problems", "Language")
    r = Language(
        pk=1,
        teacher_file="downloads/r/teacher.r",
        student_file="downloads/r/student.r",
        name="R",
        extension="r"
    )
    r.save()
    python3 = Language(
        pk=2,
        teacher_file="downloads/python/teacher.py",
        student_file="downloads/python/student.py",
        name="Python 3",
        extension="py"
    )
    python3.save()


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_default_languages),
    ]
