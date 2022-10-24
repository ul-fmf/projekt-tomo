# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def copy_institution(apps, schema_editor):
    Course = apps.get_model("courses", "Course")
    Course.objects.all().update(institution_ime=models.F("institution"))


def transfer_institutions(apps, schema_editor):
    Institution = apps.get_model("courses", "Institution")
    Course = apps.get_model("courses", "Course")
    all_institutions = set()
    for course in Course.objects.all():
        all_institutions.add(course.institution_ime)
    for institution in all_institutions:
        Institution.objects.create(name=institution)
    for institution_ob in Institution.objects.all():
        Course.objects.filter(institution_ime=institution_ob.name).update(
            institution=institution_ob
        )


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0014_coursegroup"),
    ]

    operations = [
        migrations.CreateModel(
            name="Institution",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=140)),
            ],
        ),
        migrations.AddField(
            model_name="course",
            name="institution_ime",
            field=models.CharField(default="", max_length=140),
            preserve_default=False,
        ),
        migrations.RunPython(copy_institution),
        migrations.RemoveField(
            model_name="course",
            name="institution",
        ),
        migrations.AddField(
            model_name="course",
            name="institution",
            field=models.ForeignKey(
                default=0,
                on_delete=models.deletion.CASCADE,
                related_name="institution",
                to="courses.Institution",
            ),
            preserve_default=False,
        ),
        migrations.RunPython(transfer_institutions),
        migrations.RemoveField(
            model_name="course",
            name="institution_ime",
        ),
    ]
