# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0010_remove_course_old_students"),
    ]

    operations = [
        migrations.AddField(
            model_name="studentenrollment",
            name="observed",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterUniqueTogether(
            name="studentenrollment",
            unique_together=set([("course", "user")]),
        ),
    ]
