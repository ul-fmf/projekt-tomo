from django.conf.urls import patterns, include, url
from django.contrib import admin

from rest_framework.routers import DefaultRouter

from attempts.rest import AttemptViewSet

router = DefaultRouter()
router.register(r'attempts', AttemptViewSet)

#urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'web.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

#    url(r'^admin/', include(admin.site.urls)),
#)
urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
