# Generated by Django 4.1.2 on 2022-10-28 12:49

import django.db.models.deletion
import utils.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Course",
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
                ("title", models.CharField(max_length=70)),
                ("description", models.TextField(blank=True)),
            ],
            options={
                "ordering": ["institution", "title"],
            },
        ),
        migrations.CreateModel(
            name="CourseGroup",
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
                ("title", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
            ],
        ),
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
        migrations.CreateModel(
            name="ProblemSet",
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
                ("title", models.CharField(max_length=70, verbose_name="Title")),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Description"),
                ),
                ("visible", models.BooleanField(default=False, verbose_name="Visible")),
                (
                    "solution_visibility",
                    models.CharField(
                        choices=[
                            (
                                "P",
                                "Problem descriptions and official solutions are hidden",
                            ),
                            ("H", "Official solutions are hidden"),
                            ("S", "Official solutions are visible when solved"),
                            ("V", "Official solutions are visible"),
                        ],
                        default="S",
                        max_length=20,
                        verbose_name="Solution visibility",
                    ),
                ),
            ],
            bases=(utils.models.OrderWithRespectToMixin, models.Model),
        ),
        migrations.CreateModel(
            name="StudentEnrollment",
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
                ("observed", models.BooleanField(default=True)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="courses.course"
                    ),
                ),
            ],
            options={
                "ordering": ["user", "course"],
            },
        ),
    ]
