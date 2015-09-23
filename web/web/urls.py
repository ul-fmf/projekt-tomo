from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from attempts.rest import AttemptViewSet
from problems.rest import ProblemViewSet
from courses.rest import CourseViewSet
from courses.views import homepage
import courses.urls


router = DefaultRouter()
router.register(r'attempts', AttemptViewSet, base_name='attempts')
router.register(r'problems', ProblemViewSet, base_name='problems')
router.register(r'courses', CourseViewSet, base_name='courses')


urlpatterns = patterns('',
    url(r'^$', homepage, name='homepage'),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^accounts/', include(patterns('django.contrib.auth.views',
        url(r'^login/$', 'login', {'template_name': 'login.html'}, name='login'),
        url(r'^logout/$', 'logout', name='logout'),
    ))),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include(router.urls)),
    url(r'^problems/', include('problems.urls')),
)

urlpatterns += courses.urls.urlpatterns