# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0008_problem_tags'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('attempts', '0004_historicalattempt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalattempt',
            name='part_id',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='problems.Part', null=True),
        ),
        migrations.AlterField(
            model_name='historicalattempt',
            name='user_id',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='historicalattempt',
            name='history_user',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
