from django.conf.urls import patterns, url, include
from django.contrib import admin
from courses.models import Course

admin.autodiscover()

urlpatterns = patterns('',
    # This seems wrong as it uses a template from tomo app.
    url(r'^accounts/', include(patterns('django.contrib.auth.views',
        url(r'^login/$', 'login', {
            'template_name': 'home.html',
            'extra_context': { 'courses': Course.objects }
        }),
        url(r'^logout/$', 'logout', {'next_page': '/'}),
    ))),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^courses/', include('courses.urls')),
    url(r'', include('tomo.urls')),
)
