# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Part",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("solution", models.TextField(blank=True)),
                ("validation", models.TextField(blank=True)),
                ("secret", models.TextField(default="[]")),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Problem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("title", models.CharField(max_length=70)),
                ("description", models.TextField(blank=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="part",
            name="problem",
            field=models.ForeignKey(
                related_name="parts", on_delete=models.PROTECT, to="problems.Problem"
            ),
            preserve_default=True,
        ),
        migrations.AlterOrderWithRespectTo(
            name="part",
            order_with_respect_to="problem",
        ),
    ]
