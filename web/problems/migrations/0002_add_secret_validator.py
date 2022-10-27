# -*- coding: utf-8 -*-

import utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("problems", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="part",
            name="secret",
            field=models.TextField(
                default="[]", validators=[utils.is_json_string_list]
            ),
            preserve_default=True,
        ),
    ]
