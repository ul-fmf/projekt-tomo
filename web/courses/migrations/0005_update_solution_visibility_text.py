# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0004_course_institution"),
    ]

    operations = [
        migrations.AlterField(
            model_name="problemset",
            name="solution_visibility",
            field=models.CharField(
                default=b"S",
                max_length=20,
                verbose_name="Solution visibility",
                choices=[
                    (b"H", "Official solutions are hidden"),
                    (b"S", "Official solutions are visible when solved"),
                    (b"V", "Official solutions are visible"),
                ],
            ),
        ),
    ]
