# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ('courses', '0002_auto__add_problemset__add_course'),
    )


    def forwards(self, orm):
        pass


    def backwards(self, orm):
        pass

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'courses.course': {
            'Meta': {'ordering': "['name']", 'object_name': 'Course'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'shortname': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'students': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'courses'", 'blank': 'True', 'to': u"orm['auth.User']"}),
            'teachers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'taught_courses'", 'blank': 'True', 'to': u"orm['auth.User']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'courses.problemset': {
            'Meta': {'ordering': "(u'_order',)", 'object_name': 'ProblemSet'},
            '_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'problem_sets'", 'to': u"orm['courses.Course']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'solution_visibility': ('django.db.models.fields.CharField', [], {'default': "'pogojno'", 'max_length': '20'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'visible': ('django.db.models.fields.BooleanField', [], {})
        },
        u'tomo.attempt': {
            'Meta': {'ordering': "['submission']", 'object_name': 'Attempt'},
            'active': ('django.db.models.fields.BooleanField', [], {}),
            'correct': ('django.db.models.fields.BooleanField', [], {}),
            'errors': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'part': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attempts'", 'to': u"orm['tomo.Part']"}),
            'solution': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attempts'", 'to': u"orm['tomo.Submission']"})
        },
        u'tomo.language': {
            'Meta': {'ordering': "['name']", 'object_name': 'Language'},
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'student_file': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'teacher_file': ('django.db.models.fields.CharField', [], {'max_length': '70'})
        },
        u'tomo.part': {
            'Meta': {'ordering': "(u'_order',)", 'object_name': 'Part'},
            '_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'challenge': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'problem': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parts'", 'to': u"orm['tomo.Problem']"}),
            'solution': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'validation': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'tomo.problem': {
            'Meta': {'ordering': "(u'_order',)", 'object_name': 'Problem'},
            '_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'problems'", 'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'problems'", 'to': u"orm['tomo.Language']"}),
            'preamble': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'problem_set': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'problems'", 'to': u"orm['courses.ProblemSet']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '70'})
        },
        u'tomo.submission': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Submission'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'preamble': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'problem': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'submissions'", 'to': u"orm['tomo.Problem']"}),
            'source': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'submissions'", 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['tomo', 'courses']
