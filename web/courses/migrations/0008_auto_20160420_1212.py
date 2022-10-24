# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("courses", "0007_auto_20160420_1212"),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentEnrollment",
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
                ("course", models.ForeignKey(to="courses.Course")),
                ("user", models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name="course",
            name="students",
            field=models.ManyToManyField(
                related_name="courses",
                through="courses.StudentEnrollment",
                to=settings.AUTH_USER_MODEL,
                blank=True,
            ),
        ),
    ]
