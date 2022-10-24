# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2019-04-11 04:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0012_auto_20161004_0927"),
    ]

    operations = [
        migrations.AlterField(
            model_name="problemset",
            name="solution_visibility",
            field=models.CharField(
                choices=[
                    ("P", "Problem descriptions and official solutions are hidden"),
                    ("H", "Official solutions are hidden"),
                    ("S", "Official solutions are visible when solved"),
                    ("V", "Official solutions are visible"),
                ],
                default="S",
                max_length=20,
                verbose_name="Solution visibility",
            ),
        ),
    ]
