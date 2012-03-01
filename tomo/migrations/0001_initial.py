# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Course'
        db.create_table('tomo_course', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('shortname', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('tomo', ['Course'])

        # Adding M2M table for field students on 'Course'
        db.create_table('tomo_course_students', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm['tomo.course'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('tomo_course_students', ['course_id', 'user_id'])

        # Adding M2M table for field teachers on 'Course'
        db.create_table('tomo_course_teachers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm['tomo.course'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('tomo_course_teachers', ['course_id', 'user_id'])

        # Adding model 'ProblemSet'
        db.create_table('tomo_problemset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(related_name='problem_sets', to=orm['tomo.Course'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('solution_visibility', self.gf('django.db.models.fields.CharField')(default='pogojno', max_length=20)),
            ('_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('tomo', ['ProblemSet'])

        # Adding model 'Language'
        db.create_table('tomo_language', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('student_file', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('teacher_file', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('extension', self.gf('django.db.models.fields.CharField')(max_length=4)),
        ))
        db.send_create_signal('tomo', ['Language'])

        # Adding model 'Problem'
        db.create_table('tomo_problem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='problems', to=orm['auth.User'])),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(related_name='problems', to=orm['tomo.Language'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('preamble', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('problem_set', self.gf('django.db.models.fields.related.ForeignKey')(related_name='problems', to=orm['tomo.ProblemSet'])),
            ('_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('tomo', ['Problem'])

        # Adding model 'Part'
        db.create_table('tomo_part', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('problem', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parts', to=orm['tomo.Problem'])),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('solution', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('validation', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('challenge', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('tomo', ['Part'])

        # Adding model 'Submission'
        db.create_table('tomo_submission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='submissions', to=orm['auth.User'])),
            ('problem', self.gf('django.db.models.fields.related.ForeignKey')(related_name='submissions', to=orm['tomo.Problem'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('preamble', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('source', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('tomo', ['Submission'])

        # Adding model 'Attempt'
        db.create_table('tomo_attempt', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('part', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attempts', to=orm['tomo.Part'])),
            ('submission', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attempts', to=orm['tomo.Submission'])),
            ('solution', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('errors', self.gf('django.db.models.fields.TextField')(default='{}')),
            ('correct', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('tomo', ['Attempt'])


    def backwards(self, orm):
        
        # Deleting model 'Course'
        db.delete_table('tomo_course')

        # Removing M2M table for field students on 'Course'
        db.delete_table('tomo_course_students')

        # Removing M2M table for field teachers on 'Course'
        db.delete_table('tomo_course_teachers')

        # Deleting model 'ProblemSet'
        db.delete_table('tomo_problemset')

        # Deleting model 'Language'
        db.delete_table('tomo_language')

        # Deleting model 'Problem'
        db.delete_table('tomo_problem')

        # Deleting model 'Part'
        db.delete_table('tomo_part')

        # Deleting model 'Submission'
        db.delete_table('tomo_submission')

        # Deleting model 'Attempt'
        db.delete_table('tomo_attempt')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'tomo.attempt': {
            'Meta': {'ordering': "['submission']", 'object_name': 'Attempt'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'correct': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'errors': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'part': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attempts'", 'to': "orm['tomo.Part']"}),
            'solution': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attempts'", 'to': "orm['tomo.Submission']"})
        },
        'tomo.course': {
            'Meta': {'ordering': "['name']", 'object_name': 'Course'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'shortname': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'students': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'courses'", 'blank': 'True', 'to': "orm['auth.User']"}),
            'teachers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'taught_courses'", 'blank': 'True', 'to': "orm['auth.User']"})
        },
        'tomo.language': {
            'Meta': {'ordering': "['name']", 'object_name': 'Language'},
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'student_file': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'teacher_file': ('django.db.models.fields.CharField', [], {'max_length': '70'})
        },
        'tomo.part': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'Part'},
            '_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'challenge': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'problem': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parts'", 'to': "orm['tomo.Problem']"}),
            'solution': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'validation': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'tomo.problem': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'Problem'},
            '_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'problems'", 'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'problems'", 'to': "orm['tomo.Language']"}),
            'preamble': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'problem_set': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'problems'", 'to': "orm['tomo.ProblemSet']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '70'})
        },
        'tomo.problemset': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'ProblemSet'},
            '_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'problem_sets'", 'to': "orm['tomo.Course']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'solution_visibility': ('django.db.models.fields.CharField', [], {'default': "'pogojno'", 'max_length': '20'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'tomo.submission': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Submission'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preamble': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'problem': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'submissions'", 'to': "orm['tomo.Problem']"}),
            'source': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'submissions'", 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['tomo']
