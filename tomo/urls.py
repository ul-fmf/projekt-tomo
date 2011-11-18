from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'tomo.views.homepage', {}, 'homepage'),
    (r'^settings/$', 'tomo.views.settings', {}, 'settings'),
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
            url(r'^student/$', 'student_download', name='student_download'),
            # Download the file used to solve a problem
            url(r'^(?P<user_id>\d+)/$', 'student_archive_download', name='student_archive_download'),
            # Download the file used to solve a problem
            url(r'^teacher/$', 'teacher_download', name='teacher_download'),
        ))),
        # Download the file used to solve a problem
        url(r'^api/student/$', 'api_student_contents', name='api_student_contents'),
        # Download the file used to solve a problem
        url(r'^api/teacher/$', 'api_teacher_contents', name='api_teacher_contents'),
        # Create a problem
        (r'^create/$', 'create', {}, 'create'),
        # Respond to a challenge
        (r'^upload/teacher/$', 'teacher_upload', {}, 'teacher_upload'),
        # Update the problem
        (r'^upload/student/$', 'student_upload', {}, 'student_upload'),
    ))),
)