# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attempts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='attempt',
            old_name='accepted',
            new_name='valid',
        ),
    ]
