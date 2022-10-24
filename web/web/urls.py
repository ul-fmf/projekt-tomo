import courses.urls
import django.contrib.auth.views
from attempts.rest import AttemptViewSet
from courses.rest import CourseViewSet, ProblemSetViewSet
from courses.views import homepage
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from problems.rest import ProblemViewSet
from rest_framework.routers import DefaultRouter
from users.views import mobile_app_token
from utils.views import help, privacy_policy, terms_of_service

router = DefaultRouter()
router.register(r"attempts", AttemptViewSet, base_name="attempts")
router.register(r"problems", ProblemViewSet, base_name="problems")
router.register(r"problem_sets", ProblemSetViewSet, base_name="problem_sets")
router.register(r"courses", CourseViewSet, base_name="courses")


urlpatterns = [
    url(r"^$", homepage, name="homepage"),
    url(r"^terms_of_service$", terms_of_service, name="terms_of_service"),
    url(r"^privacy_policy$", privacy_policy, name="privacy_policy"),
    url(r"^help$", help, name="help"),
    url(r"^help/students$", help, {"special": "students"}, name="help_students"),
    url(r"^help/teachers$", help, {"special": "teachers"}, name="help_teachers"),
    url("", include("social_django.urls", namespace="social")),
    url(
        r"^accounts/",
        include(
            [
                url(
                    r"^login/$",
                    django.contrib.auth.views.login,
                    {"template_name": "login.html"},
                    name="login",
                ),
                url(r"^logout/$", django.contrib.auth.views.logout, name="logout"),
            ]
        ),
    ),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^api/auth/", include("rest_framework.urls", namespace="rest_framework")),
    url(r"^api/mobile-app-token/", mobile_app_token, name="mobile_app_token"),
    url(r"^api/", include(router.urls)),
    url(r"^problems/", include("problems.urls")),
    url(r"^statistics/", include("tomo_statistics.urls")),
]

urlpatterns += courses.urls.urlpatterns

if "silk" in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r"^silk/", include("silk.urls", namespace="silk")),
    ]
