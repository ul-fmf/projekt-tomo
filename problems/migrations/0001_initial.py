# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=70)),
                ('student_file', models.CharField(max_length=70)),
                ('teacher_file', models.CharField(max_length=70)),
                ('extension', models.CharField(max_length=4)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Part',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('description', models.TextField(blank=True)),
                ('solution', models.TextField(blank=True)),
                ('validation', models.TextField(blank=True)),
                ('challenge', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('title', models.CharField(max_length=70)),
                ('description', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('preamble', models.TextField(blank=True)),
                ('author', models.ForeignKey(related_name='problems', to=settings.AUTH_USER_MODEL)),
                ('language', models.ForeignKey(related_name='problems', to='problems.Language')),
                ('problem_set', models.ForeignKey(related_name='problems', to='courses.ProblemSet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterOrderWithRespectTo(
            name='problem',
            order_with_respect_to='problem_set',
        ),
        migrations.AddField(
            model_name='part',
            name='problem',
            field=models.ForeignKey(related_name='parts', to='problems.Problem'),
            preserve_default=True,
        ),
        migrations.AlterOrderWithRespectTo(
            name='part',
            order_with_respect_to='problem',
        ),
    ]
