from django.conf.urls.defaults import *

urlpatterns = patterns('tomo.views',
    # Download the file used to solve a problem
    (r'(?P<problem_id>\d+)/(?P<user_id>\d+)/', 'download_user', {}, 'download_user'),
    # Download the file used to solve a problem
    (r'(?P<problem_id>\d+)/edit/', 'edit', {}, 'edit'),
    # Download the file used to solve a problem
    (r'(?P<problem_id>\d+)/', 'download', {}, 'download'),
    # Respond to a challenge
    (r'^upload/$', 'upload', {}, 'upload'),
    # Download the file used to edit a newly created problem
    (r'^create/$', 'edit', {}, 'create'),
    # Update the problem
    (r'^update/$', 'update', {}, 'update'),
)
