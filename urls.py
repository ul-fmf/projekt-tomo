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
    url(r'^accounts/logout/(?P<next_page>.*)/$',
     'django.contrib.auth.views.logout', name='logout_next_page'),
)

urlpatterns += patterns('tomo.problem.views',
    url(r'^$', 'problem_list', name='problem_list'),
    url(r'^problem/(?P<object_id>\d+)/$', 'problem', name='show_problem'),
    url(r'^problem/(?P<object_id>\d+)/download/$', 'download_problem',
        name='download_problem'),
    url(r'^problem/(?P<object_id>\d+)/upload/$', 'upload_solution',
        name='upload_solution'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT
        }),
    )
