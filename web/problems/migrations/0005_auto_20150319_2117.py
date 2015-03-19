# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0004_auto_20150319_2117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='problem_set',
            field=models.ForeignKey(related_name='problems', to='courses.ProblemSet', null=True),
            preserve_default=True,
        ),
    ]
