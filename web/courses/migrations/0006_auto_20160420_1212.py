# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0005_update_solution_visibility_text"),
    ]

    operations = [
        migrations.RenameField(
            model_name="course",
            old_name="students",
            new_name="old_students",
        ),
    ]
