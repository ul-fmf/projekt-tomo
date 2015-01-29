# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import utils


class Migration(migrations.Migration):

    dependencies = [
        ('attempts', '0002_rename_accepted_to_valid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attempt',
            name='feedback',
            field=models.TextField(default=b'[]', validators=[utils.is_json_string_list]),
            preserve_default=True,
        ),
    ]
