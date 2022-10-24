# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("problems", "0010_auto_20160118_1046"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalproblem",
            name="language",
            field=models.CharField(
                default=b"python",
                max_length=8,
                choices=[(b"python", b"Python 3"), (b"octave", b"Octave")],
            ),
        ),
        migrations.AddField(
            model_name="problem",
            name="language",
            field=models.CharField(
                default=b"python",
                max_length=8,
                choices=[(b"python", b"Python 3"), (b"octave", b"Octave")],
            ),
        ),
    ]
