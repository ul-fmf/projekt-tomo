# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Renaming model 'Course'
        db.rename_table(u'tomo_course', u'courses_course')

        # Renaming model 'ProblemSet'
        db.rename_table(u'tomo_problemset', u'courses_problemset')

        # Renaming M2M table for field students on 'Course'
        db.rename_table(db.shorten_name(u'tomo_course_students'), db.shorten_name(u'courses_course_students'))

        # Renaming M2M table for field teachers on 'Course'
        db.rename_table(db.shorten_name(u'tomo_course_teachers'), db.shorten_name(u'courses_course_teachers'))


    def backwards(self, orm):
        # Renaming model 'Course'
        db.rename_table(u'courses_course', u'tomo_course')

        # Renaming model 'ProblemSet'
        db.rename_table(u'courses_problemset', u'tomo_problemset')

        # Renaming M2M table for field students on 'Course'
        db.rename_table(db.shorten_name(u'courses_course_students'), db.shorten_name(u'tomo_course_students'))

        # Renaming M2M table for field teachers on 'Course'
        db.rename_table(db.shorten_name(u'courses_course_teachers'), db.shorten_name(u'tomo_course_teachers'))
