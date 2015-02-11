from django.conf.urls import patterns, url
from problems import views

urlpatterns = patterns('',
    url(r'^$', views.problem_list, name='problem_list'),
    # ex: /problems/5/
    url(r'^(?P<problem_pk>\d+)/$', views.problem_detail, name='problem_detail'),
    url(r'^(?P<problem_pk>\d+)/download/$', views.problem_attempt_file, name='problem_attempt_file'),
)
