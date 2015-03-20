from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from attempts.rest import AttemptViewSet
from problems.rest import ProblemViewSet
from problems.views import problem_list


router = DefaultRouter()
router.register(r'attempts', AttemptViewSet)
router.register(r'problems', ProblemViewSet)


urlpatterns = patterns('',
    url(r'^$', problem_list),
    url(r'^accounts/', include(patterns('django.contrib.auth.views',
        url(r'^login/$', 'login', {'template_name': 'login.html'}, name='login'),
        url(r'^logout/$', 'logout', name='logout'),
    ))),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include(router.urls)),
    url(r'^problems/', include('problems.urls')),
)
