# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-11-04 13:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("problems", "0016_auto_20170907_1121"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="historicalproblem",
            name="verify_attempt_tokens",
        ),
        migrations.RemoveField(
            model_name="problem",
            name="verify_attempt_tokens",
        ),
    ]
