# Generated by Django 4.1.2 on 2022-10-28 12:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("problems", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("attempts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalattempt",
            name="history_user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="historicalattempt",
            name="part",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="problems.part",
            ),
        ),
        migrations.AddField(
            model_name="historicalattempt",
            name="user",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="attempt",
            name="part",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="attempts",
                to="problems.part",
            ),
        ),
        migrations.AddField(
            model_name="attempt",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="attempts",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="attempt",
            unique_together={("user", "part")},
        ),
    ]
