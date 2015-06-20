from django.conf.urls import patterns, url
from . import views
from views import ProblemSetCreate


urlpatterns = patterns(
    '',
    url(r'^problem_set/(?P<problem_set_pk>\d+)/$',
        views.problem_set_detail,
        name='problem_set_detail'),
    url(r'^problem_set/(?P<problem_set_pk>\d+)/download/$',
        views.problem_set_attempts,
        name='problem_set_attempts'),
    url(r'^problem_set/(?P<problem_set_pk>\d+)/move/(?P<shift>-?\d+)/$',
        views.problem_set_move,
        name='problem_set_move'),
    url(r'^problem_set/(?P<problem_set_pk>\d+)/toggle_visible/$',
        views.problem_set_toggle_visible,
        name='problem_set_toggle_visible'),
    url(r'^problem_set/(?P<problem_set_pk>\d+)/toggle_solution_visibility/$',
        views.problem_set_toggle_solution_visibility,
        name='problem_set_toggle_solution_visibility'),
    url(r'^create/(?P<course_pk>\d+)/$',
        ProblemSetCreate.as_view(),
        name='problem_set_create'),
    url(r'^course/(?P<course_pk>\d+)/$',
        views.course_detail,
        name='course_detail'),
)
