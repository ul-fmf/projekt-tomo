# -*- coding: utf-8 -*-

import django.db.models.deletion
import utils
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("problems", "0002_add_secret_validator"),
    ]

    operations = [
        migrations.CreateModel(
            name="HistoricalPart",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        verbose_name="ID", db_index=True, auto_created=True, blank=True
                    ),
                ),
                (
                    "problem_id",
                    models.IntegerField(db_index=True, null=True, blank=True),
                ),
                ("description", models.TextField(blank=True)),
                ("solution", models.TextField(blank=True)),
                ("validation", models.TextField(blank=True)),
                (
                    "secret",
                    models.TextField(
                        default="[]", validators=[utils.is_json_string_list]
                    ),
                ),
                ("_order", models.IntegerField(editable=False)),
                ("history_id", models.AutoField(serialize=False, primary_key=True)),
                ("history_date", models.DateTimeField()),
                (
                    "history_type",
                    models.CharField(
                        max_length=1,
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                    ),
                ),
            ],
            options={
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": "history_date",
                "verbose_name": "historical part",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="HistoricalProblem",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        verbose_name="ID", db_index=True, auto_created=True, blank=True
                    ),
                ),
                ("title", models.CharField(max_length=70)),
                ("description", models.TextField(blank=True)),
                ("history_id", models.AutoField(serialize=False, primary_key=True)),
                ("history_date", models.DateTimeField()),
                (
                    "history_type",
                    models.CharField(
                        max_length=1,
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                    ),
                ),
            ],
            options={
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": "history_date",
                "verbose_name": "historical problem",
            },
            bases=(models.Model,),
        ),
    ]
