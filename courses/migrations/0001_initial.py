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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=70)),
                ('description', models.TextField(blank=True)),
                ('visible', models.BooleanField(default=False)),
                ('solution_visibility', models.CharField(default=b'pogojno', max_length=20, choices=[(b'skrite', b'skrite'), (b'pogojno', b'vidne, ko je naloga re\xc5\xa1ena'), (b'vidne', b'vidne')])),
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
