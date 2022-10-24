# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("attempts", "0005_auto_20160118_1045"),
    ]

    operations = [
        migrations.RenameField(
            model_name="historicalattempt",
            old_name="part_id",
            new_name="part",
        ),
        migrations.RenameField(
            model_name="historicalattempt",
            old_name="user_id",
            new_name="user",
        ),
    ]
