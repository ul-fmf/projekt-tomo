# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Course",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("title", models.CharField(max_length=70)),
                ("description", models.TextField(blank=True)),
                (
                    "students",
                    models.ManyToManyField(
                        related_name="courses", to=settings.AUTH_USER_MODEL, blank=True
                    ),
                ),
                (
                    "teachers",
                    models.ManyToManyField(
                        related_name="taught_courses",
                        to=settings.AUTH_USER_MODEL,
                        blank=True,
                    ),
                ),
            ],
            options={
                "ordering": ["title"],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ProblemSet",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("title", models.CharField(max_length=70)),
                ("description", models.TextField(blank=True)),
                ("visible", models.BooleanField(default=False)),
                (
                    "solution_visibility",
                    models.CharField(
                        default="S",
                        max_length=20,
                        choices=[
                            ("H", "Hidden"),
                            ("S", "Visible when solved"),
                            ("V", "Visible"),
                        ],
                    ),
                ),
                (
                    "course",
                    models.ForeignKey(
                        related_name="problem_sets",
                        on_delete=models.PROTECT,
                        to="courses.Course",
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AlterOrderWithRespectTo(
            name="problemset",
            order_with_respect_to="course",
        ),
    ]
