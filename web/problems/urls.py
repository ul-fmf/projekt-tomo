from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns('',
    url(r'^(?P<problem_pk>\d+)/solutions/$', views.problem_solution, name='problem_solution'),
    url(r'^(?P<problem_pk>\d+)/download/$', views.problem_attempt_file, name='problem_attempt_file'),
    url(r'^(?P<problem_pk>\d+)/edit/$', views.problem_edit_file, name='problem_edit_file'),
)
