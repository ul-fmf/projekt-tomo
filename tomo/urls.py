from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'tomo.views.homepage', {}, 'homepage'),
    (r'^course/', include(patterns('tomo.views',
        url(r'^(?P<course_id>\d+)/$', 'view_course', name='course'),
    ))),
    (r'^problem_set/', include(patterns('tomo.views',
        (r'^(?P<problem_set_id>\d+)/', include(patterns('tomo.views.problem_set',
            url(r'^$', 'view_problem_set', name='problem_set'),
            url(r'^zip/$', 'download_problem_set', name='download_problem_set'),
            url(r'^stats/$', 'view_statistics', name='view_statistics'),
        ))),
    ))),
    (r'^problem/', include(patterns('tomo.views.problem',
        (r'^(?P<problem_id>\d+)/', include(patterns('tomo.views.problem',
            # Download the file used to solve a problem
            (r'^$', 'download', {}, 'download'),
            # Download the file used to solve a problem
            (r'^(?P<user_id>\d+)/$', 'download_user', {}, 'download_user'),
            # Download the file used to solve a problem
            (r'^edit/$', 'edit', {}, 'edit'),
        ))),
        # Respond to a challenge
        (r'^upload/$', 'upload', {}, 'upload'),
        # Download the file used to edit a problem
        (r'^edit/$', 'edit', {}, 'edit'),
        # Create a problem
        (r'^create/$', 'create', {}, 'create'),
        # Update the problem
        (r'^update/$', 'update', {}, 'update'),
    ))),
)