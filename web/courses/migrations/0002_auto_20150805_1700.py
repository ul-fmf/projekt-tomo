# -*- coding: utf-8 -*-

import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("taggit", "0001_initial"),
        ("courses", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="tags",
            field=taggit.managers.TaggableManager(
                to="taggit.Tag",
                through="taggit.TaggedItem",
                help_text="A comma-separated list of tags.",
                verbose_name="Tags",
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="problemset",
            name="tags",
            field=taggit.managers.TaggableManager(
                to="taggit.Tag",
                through="taggit.TaggedItem",
                help_text="A comma-separated list of tags.",
                verbose_name="Tags",
            ),
            preserve_default=True,
        ),
    ]
