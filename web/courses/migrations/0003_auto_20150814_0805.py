# -*- coding: utf-8 -*-

import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0002_auto_20150805_1700"),
    ]

    operations = [
        migrations.AlterField(
            model_name="course",
            name="tags",
            field=taggit.managers.TaggableManager(
                to="taggit.Tag",
                through="taggit.TaggedItem",
                blank=True,
                help_text="A comma-separated list of tags.",
                verbose_name="Tags",
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="problemset",
            name="description",
            field=models.TextField(verbose_name="Description", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="problemset",
            name="solution_visibility",
            field=models.CharField(
                default="S",
                max_length=20,
                verbose_name="Solution visibility",
                choices=[
                    ("H", "Hidden"),
                    ("S", "Visible when solved"),
                    ("V", "Visible"),
                ],
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="problemset",
            name="tags",
            field=taggit.managers.TaggableManager(
                to="taggit.Tag",
                through="taggit.TaggedItem",
                blank=True,
                help_text="A comma-separated list of tags.",
                verbose_name="Tags",
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="problemset",
            name="title",
            field=models.CharField(max_length=70, verbose_name="Title"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="problemset",
            name="visible",
            field=models.BooleanField(default=False, verbose_name="Visible"),
            preserve_default=True,
        ),
    ]
