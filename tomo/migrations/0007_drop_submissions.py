# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_table(u'tomo_submission', u'submissions_submission')
        db.rename_table(u'tomo_attempt', u'submissions_attempt')


    def backwards(self, orm):
        db.rename_table(u'submissions_submission', u'tomo_submission')
        db.rename_table(u'submissions_attempt', u'tomo_attempt')


    models = {
        
    }

    complete_apps = ['tomo']
