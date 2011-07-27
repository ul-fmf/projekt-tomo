from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

from tomo.problem.models import Problem, Part


admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {
        'template_name': 'login.html'
    }, 'login'),
    url(r'^accounts/logout/$',
     'django.contrib.auth.views.logout', name='logout'),
)

urlpatterns += patterns('tomo.problem.views',
    url(r'^$', 'collection_list', name='collection_list'),
    url(r'^problem/(?P<object_id>\d+)/$', 'problem', name='show_problem'),
    url(r'^problem/(?P<object_id>\d+)/download/$', 'download_problem',
        name='download_problem'),
    url(r'^problem/(?P<object_id>\d+)/solutions/$', 'solutions',
        name='solutions'),
    url(r'^problem/(?P<object_id>\d+)/solutions/(?P<user_id>\d+)/$', 'download_user_solutions',
        name='download_user_solutions'),
    url(r'^problem/(?P<object_id>\d+)/download_anonymous/$', 'download_anonymous_problem',
        name='download_anonymous_problem'),
    url(r'^problem/(?P<object_id>\d+)/edit/$', 'edit_problem',
        name='edit_problem'),
    url(r'^problem/(?P<object_id>\d+)/upload/$', 'upload_solution',
        name='upload_solution'),
    url(r'^problem/(?P<object_id>\d+)/crazy_upload/$', 'upload_problem',
        name='upload_problem'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT
        }),
    )
