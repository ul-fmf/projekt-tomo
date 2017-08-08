# -*- coding: utf-8 -*-

from django.db import models, migrations
import utils


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='part',
            name='secret',
            field=models.TextField(default=b'[]', validators=[utils.is_json_string_list]),
            preserve_default=True,
        ),
    ]
