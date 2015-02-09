from django.conf.urls import patterns, url

from problems import views

urlpatterns = patterns('',
    url(r'^$', views.problem_list, name='problem_list'),
    # ex: /problems/5/
    url(r'^(?P<problem_id>\d+)/$', views.problem_detail, name='problem_detail'),
    url(r'^(?P<problem_id>\d+)/download$', views.return_problem_file, name='problem_download'),
)