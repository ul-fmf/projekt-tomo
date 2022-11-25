import courses.urls
import django.contrib.auth.views
from attempts.rest import AttemptViewSet
from courses.rest import CourseViewSet, ProblemSetViewSet
from courses.views import homepage
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from problems.rest import ProblemViewSet
from rest_framework.routers import DefaultRouter
from users.views import mobile_app_token
from utils.views import help, privacy_policy, terms_of_service

router = DefaultRouter()
router.register(r"attempts", AttemptViewSet, basename="attempts")
router.register(r"problems", ProblemViewSet, basename="problems")
router.register(r"problem_sets", ProblemSetViewSet, basename="problem_sets")
router.register(r"courses", CourseViewSet, basename="courses")


urlpatterns = [
    path("", homepage, name="homepage"),
    path("terms_of_service", terms_of_service, name="terms_of_service"),
    path("privacy_policy", privacy_policy, name="privacy_policy"),
    path("help", help, name="help"),
    path("help/students", help, {"special": "students"}, name="help_students"),
    path("help/teachers", help, {"special": "teachers"}, name="help_teachers"),
    path("", include("social_django.urls", namespace="social")),
    path(
        "accounts/",
        include(
            [
                path(
                    r"login/",
                    django.contrib.auth.views.LoginView.as_view(),
                    {"template_name": "login.html"},
                    name="login",
                ),
                path(
                    "logout/",
                    django.contrib.auth.views.LogoutView.as_view(),
                    name="logout",
                ),
            ]
        ),
    ),
    path("admin/", admin.site.urls),
    path("api/auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("api/mobile-app-token/", mobile_app_token, name="mobile_app_token"),
    path("api/", include(router.urls)),
    path("problems/", include("problems.urls")),
    path("statistics/", include("tomo_statistics.urls")),
]

urlpatterns += courses.urls.urlpatterns

if "silk" in settings.INSTALLED_APPS:
    urlpatterns += [
        path("silk/", include("silk.urls", namespace="silk")),
    ]
