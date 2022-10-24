# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("problems", "0006_auto_20150322_1945"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalproblem",
            name="_order",
            field=models.IntegerField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AlterOrderWithRespectTo(
            name="problem",
            order_with_respect_to="problem_set",
        ),
    ]
