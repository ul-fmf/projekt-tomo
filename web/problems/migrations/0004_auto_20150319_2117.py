# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
        ('problems', '0003_historicalpart_historicalproblem'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalproblem',
            name='problem_set_id',
            field=models.IntegerField(db_index=True, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='problem',
            name='problem_set',
            field=models.ForeignKey(related_name='problem', to='courses.ProblemSet', null=True),
            preserve_default=True,
        ),
    ]
