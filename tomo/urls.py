from django.conf import settings
from django.conf.urls import patterns, url, include
from .views.problem import PartDelete, ProblemCreate, ProblemDelete, ProblemUpdate

urlpatterns = patterns('',
    url(r'^$', 'tomo.views.homepage', name='homepage'),
    url(r'^settings/$', 'tomo.views.settings', name='settings'),
    (r'^problem_set/', include(patterns('tomo.views.problem_set',
        (r'^(?P<problem_set_id>\d+)/', include(patterns('tomo.views.problem_set',
            url(r'^$', 'view_problem_set', name='problem_set'),
            url(r'^student/$', 'student_zip', name='student_zip'),
            url(r'^teacher/$', 'teacher_zip', name='teacher_zip'),
            url(r'^stats/(?P<limit>\d+)$', 'view_statistics', name='view_statistics'),
            url(r'^results/$', 'results_zip', name='results_zip'),
        ))),
        url(r'^create/$', 'create', name='create_set'),
    ))),
    (r'^problem/', include(patterns('tomo.views.problem',
        (r'^(?P<pk>\d+)/', include(patterns('tomo.views.problem',
            url(r'^student/$', 'student_download', name='student_download'),
            url(r'^(?P<user_id>\d+)/$', 'student_archive_download', name='student_archive_download'),
            url(r'^(?P<user_id>\d+)/history/$', 'student_history_download', name='student_history_download'),
            url(r'^teacher/$', 'teacher_download', name='teacher_download'),
            url(r'^move/(?P<shift>-?\d+)/$', 'move', name='move_problem'),
            url(r'^delete/$', ProblemDelete.as_view(), name='problem_delete'),
            url(r'^update/$', ProblemUpdate.as_view(), name='problem_update'),
        ))),
        url(r'^api/student/$', 'api_student_contents', name='api_student_contents'),
        url(r'^api/teacher/$', 'api_teacher_contents', name='api_teacher_contents'),
        url(r'^copy/$', 'copy', name='copy'),
        url(r'^create/(?P<problem_set_id>\d+)/$', ProblemCreate.as_view(), name='problem_create'),
        url(r'^upload/teacher/$', 'teacher_upload', name='teacher_upload'),
        url(r'^upload/student/$', 'student_upload', name='student_upload'),
    ))),
    (r'^part/', include(patterns('tomo.views.problem',
        (r'^(?P<pk>\d+)/', include(patterns('tomo.views.problem',
            url(r'^delete/$', PartDelete.as_view(), name='part_delete')
        )))
    )))
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
