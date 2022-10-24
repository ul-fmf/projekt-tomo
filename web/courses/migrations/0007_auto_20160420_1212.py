# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0006_auto_20160420_1212"),
    ]

    operations = [
        migrations.AlterField(
            model_name="course",
            name="old_students",
            field=models.ManyToManyField(
                related_name="old_courses", to=settings.AUTH_USER_MODEL, blank=True
            ),
        ),
    ]
