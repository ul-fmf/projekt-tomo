from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^(?P<course_pk>\d+)$',
        views.course_statistics,
        name='statistics_landing_page'),
    url(r'^(?P<course_pk>\d+)/submission_history$',
        views.course_submission_history,
        name='statistics_submission_history'),
    url(r'^(?P<course_pk>\d+)/submission_history/(?P<problemset_pk>\d+)$',
        views.course_submission_history_problemset,
        name='statistics_submission_history_problemset'),
    
    url(r'^(?P<course_pk>\d+)/submission_history/(?P<problemset_pk>\d+)/(?P<user_pk>\d+)$',
        views.course_user_submission_history_problemset,
        name='statistics_submission_history_problemset_user'),
]
