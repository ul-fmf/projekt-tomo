from django.conf.urls import patterns, url
from problems import views


urlpatterns = patterns('',
    url(r'^welcome/$', views.welcome, name='welcome'),
    #url(r'^$', views.not_yet_enrolled, name='not_yet_enrolled'),
    #url(r'^$', views.course_list, name='course_list'),
    #url(r'^$', views.my_courses, name='my_courses'),
    #url(r'^$', views.assembly_list, name='assembly_list'),
    url(r'^problem_list/$', views.problem_list, name='problem_list'),
    # ex: /problems/5/
    #url(r'^(?P<problem_pk>\d+)/$', views.problem_detail, name='problem_detail'),
    url(r'^(?P<problem_pk>\d+)/$', views.problem_solution, name='problem_solution'),
    url(r'^(?P<problem_pk>\d+)/download/$', views.problem_attempt_file, name='problem_attempt_file'),
)
