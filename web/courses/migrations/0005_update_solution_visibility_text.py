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
                default="S",
                max_length=20,
                verbose_name="Solution visibility",
                choices=[
                    ("H", "Official solutions are hidden"),
                    ("S", "Official solutions are visible when solved"),
                    ("V", "Official solutions are visible"),
                ],
            ),
        ),
    ]
