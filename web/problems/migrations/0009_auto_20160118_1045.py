# -*- coding: utf-8 -*-

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0005_update_solution_visibility_text"),
        ("problems", "0008_problem_tags"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicalpart",
            name="problem_id",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.DO_NOTHING,
                db_constraint=False,
                blank=True,
                to="problems.Problem",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="historicalproblem",
            name="problem_set_id",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.DO_NOTHING,
                db_constraint=False,
                blank=True,
                to="courses.ProblemSet",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="historicalpart",
            name="history_user",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="historicalproblem",
            name="history_user",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
        ),
    ]
