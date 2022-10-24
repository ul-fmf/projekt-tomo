# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0009_auto_20160420_1214"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="course",
            name="old_students",
        ),
    ]
