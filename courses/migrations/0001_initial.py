# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=70)),
                ('description', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('students', models.ManyToManyField(related_name='courses', to=settings.AUTH_USER_MODEL, blank=True)),
                ('teachers', models.ManyToManyField(related_name='taught_courses', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProblemSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('title', models.CharField(max_length=70)),
                ('description', models.TextField(blank=True)),
                ('visible', models.BooleanField(default=False)),
                ('solution_visibility', models.CharField(max_length=20, choices=[('skrite', 'skrite'), ('pogojno', 'vidne, ko je naloga rešena'), ('vidne', 'vidne')], default='pogojno')),
                ('timestamp', models.DateTimeField(auto_now=True, db_index=True)),
                ('course', models.ForeignKey(related_name='problem_sets', to='courses.Course')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterOrderWithRespectTo(
            name='problemset',
            order_with_respect_to='course',
        ),
    ]
