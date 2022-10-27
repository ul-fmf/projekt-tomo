# -*- coding: utf-8 -*-

import utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("attempts", "0002_rename_accepted_to_valid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attempt",
            name="feedback",
            field=models.TextField(
                default="[]", validators=[utils.is_json_string_list]
            ),
            preserve_default=True,
        ),
    ]
