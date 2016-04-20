# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_auto_20160420_1212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='old_students',
            field=models.ManyToManyField(related_name='old_courses', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
