from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'^$', 'tomo.views.homepage', name='homepage'),
    url(r'^settings/$', 'tomo.views.settings', name='settings'),
    (r'^problem_set/', include(patterns('tomo.views',
        (r'^(?P<problem_set_id>\d+)/', include(patterns('tomo.views.problem_set',
            url(r'^$', 'view_problem_set', name='problem_set'),
            url(r'^student/$', 'student_zip', name='student_zip'),
            url(r'^teacher/$', 'teacher_zip', name='teacher_zip'),
            url(r'^stats/(?P<limit>\d+)$', 'view_statistics', name='view_statistics'),
            url(r'^toggle_solution_visibility/$', 'toggle_solution_visibility', name='toggle_solution_visibility'),
            url(r'^toggle_visible/$', 'toggle_visible', name='toggle_visible'),
            url(r'^move/(?P<shift>-?\d+)/$', 'move', name='move_problem_set'),
            url(r'^results/$', 'results_csv', name='results_csv'),
        ))),
    ))),
    (r'^problem/', include(patterns('tomo.views.problem',
        (r'^(?P<problem_id>\d+)/', include(patterns('tomo.views.problem',
            url(r'^student/$', 'student_download', name='student_download'),
            url(r'^(?P<user_id>\d+)/$', 'student_archive_download', name='student_archive_download'),
            url(r'^(?P<user_id>\d+)/history/$', 'student_history_download', name='student_history_download'),
            url(r'^teacher/$', 'teacher_download', name='teacher_download'),
            url(r'^moss/$', 'moss_zip', name='moss_zip'),
            url(r'^mass/$', 'mass_zip', name='mass_zip'),
            url(r'^move/(?P<shift>-?\d+)/$', 'move', name='move_problem'),
        ))),
        url(r'^api/student/$', 'api_student_contents', name='api_student_contents'),
        url(r'^api/teacher/$', 'api_teacher_contents', name='api_teacher_contents'),
        url(r'^create/$', 'create', name='create'),
        url(r'^copy/$', 'copy', name='copy'),
        url(r'^upload/teacher/$', 'teacher_upload', name='teacher_upload'),
        url(r'^upload/student/$', 'student_upload', name='student_upload'),
    ))),
)