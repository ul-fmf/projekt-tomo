# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("problems", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Attempt",
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
                ("solution", models.TextField(blank=True)),
                ("accepted", models.BooleanField(default=False)),
                ("feedback", models.TextField(blank=True)),
                (
                    "part",
                    models.ForeignKey(related_name="attempts", to="problems.Part"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        related_name="attempts", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name="attempt",
            unique_together=set([("user", "part")]),
        ),
    ]
