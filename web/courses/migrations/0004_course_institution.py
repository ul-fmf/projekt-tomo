# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0003_auto_20150814_0805"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="institution",
            field=models.CharField(
                default="Fakulteta za matematiko in fiziko", max_length=140
            ),
            preserve_default=False,
        ),
    ]
