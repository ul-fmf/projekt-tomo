# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("problems", "0009_auto_20160118_1045"),
    ]

    operations = [
        migrations.RenameField(
            model_name="historicalpart",
            old_name="problem_id",
            new_name="problem",
        ),
        migrations.RenameField(
            model_name="historicalproblem",
            old_name="problem_set_id",
            new_name="problem_set",
        ),
    ]
