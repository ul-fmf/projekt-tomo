from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from attempts.rest import AttemptViewSet
from problems.rest import ProblemViewSet


router = DefaultRouter()
router.register(r'attempt', AttemptViewSet)
router.register(r'problem', ProblemViewSet)

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^', include(router.urls)),
    url(r'^problems/', include('problems.urls')),
)
