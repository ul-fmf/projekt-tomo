# Generated by Django 4.1.2 on 2022-10-28 12:49

import django.db.models.deletion
import simple_history.models
import taggit.managers
import utils
import utils.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("taggit", "0005_auto_20220424_2025"),
        ("courses", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="HistoricalPart",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("template", models.TextField(blank=True)),
                ("solution", models.TextField(blank=True)),
                ("validation", models.TextField(blank=True)),
                (
                    "secret",
                    models.TextField(
                        default="[]", validators=[utils.is_json_string_list]
                    ),
                ),
                ("_order", models.IntegerField(editable=False)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical part",
                "verbose_name_plural": "historical parts",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalProblem",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("title", models.CharField(max_length=70)),
                ("description", models.TextField(blank=True)),
                (
                    "language",
                    models.CharField(
                        choices=[
                            ("python", "Python 3"),
                            ("octave", "Octave/Matlab"),
                            ("r", "R"),
                        ],
                        default="python",
                        max_length=8,
                    ),
                ),
                ("_order", models.IntegerField(editable=False)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical problem",
                "verbose_name_plural": "historical problems",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="Problem",
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
                (
                    "language",
                    models.CharField(
                        choices=[
                            ("python", "Python 3"),
                            ("octave", "Octave/Matlab"),
                            ("r", "R"),
                        ],
                        default="python",
                        max_length=8,
                    ),
                ),
                (
                    "problem_set",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="problems",
                        to="courses.problemset",
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        blank=True,
                        help_text="A comma-separated list of tags.",
                        through="taggit.TaggedItem",
                        to="taggit.Tag",
                        verbose_name="Tags",
                    ),
                ),
            ],
            bases=(utils.models.OrderWithRespectToMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Part",
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
                ("description", models.TextField(blank=True)),
                ("template", models.TextField(blank=True)),
                ("solution", models.TextField(blank=True)),
                ("validation", models.TextField(blank=True)),
                (
                    "secret",
                    models.TextField(
                        default="[]", validators=[utils.is_json_string_list]
                    ),
                ),
                (
                    "problem",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="parts",
                        to="problems.problem",
                    ),
                ),
            ],
            bases=(utils.models.OrderWithRespectToMixin, models.Model),
        ),
    ]
