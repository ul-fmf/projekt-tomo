# -*- coding: utf-8 -*-

import django.db.models.deletion
import utils
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("attempts", "0003_make_feedback_string_list"),
    ]

    operations = [
        migrations.CreateModel(
            name="HistoricalAttempt",
            fields=[
                (
                    "id",
                    models.IntegerField(
                        verbose_name="ID", db_index=True, auto_created=True, blank=True
                    ),
                ),
                ("user_id", models.IntegerField(db_index=True, null=True, blank=True)),
                ("part_id", models.IntegerField(db_index=True, null=True, blank=True)),
                ("solution", models.TextField(blank=True)),
                ("valid", models.BooleanField(default=False)),
                (
                    "feedback",
                    models.TextField(
                        default="[]", validators=[utils.is_json_string_list]
                    ),
                ),
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
                "verbose_name": "historical attempt",
            },
            bases=(models.Model,),
        ),
    ]
