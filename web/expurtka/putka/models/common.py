from django.db import models


class UntabledItem(models.Model):
	key = models.CharField(max_length=128, db_index=True, primary_key=True)
	value = models.TextField(null=True, blank=True)
