# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("attempts", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="attempt",
            old_name="accepted",
            new_name="valid",
        ),
    ]
