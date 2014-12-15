# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attempt',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('solution', models.TextField(blank=True)),
                ('errors', models.TextField(default=b'{}')),
                ('correct', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=False)),
                ('part', models.ForeignKey(related_name='attempts', to='problems.Part')),
            ],
            options={
                'ordering': ['submission'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip', models.IPAddressField()),
                ('preamble', models.TextField(blank=True)),
                ('problem', models.ForeignKey(related_name='submissions', to='problems.Problem')),
                ('user', models.ForeignKey(related_name='submissions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='attempt',
            name='submission',
            field=models.ForeignKey(related_name='attempts', to='submissions.Submission'),
            preserve_default=True,
        ),
    ]
