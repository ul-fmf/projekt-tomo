# -*- coding: utf-8 -*-

import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("taggit", "0001_initial"),
        ("problems", "0007_auto_20150324_0826"),
    ]

    operations = [
        migrations.AddField(
            model_name="problem",
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
    ]
