from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from attempts.rest import AttemptViewSet


router = DefaultRouter()
router.register(r'attempts', AttemptViewSet)

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^', include(router.urls)),
)
