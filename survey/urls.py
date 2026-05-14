from django.urls import path, include
from .views import CheckAdminStatus
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"surveys", views.SurveyViewSet, basename="survey")

urlpatterns = [
    path("list/", views.list_surveys, name="list_surveys"),
    path(
        "get_survey/", views.get_questions_and_options, name="get_questions_and_options"
    ),
    path("check-admin-status/", CheckAdminStatus.as_view(), name="check_admin_status"),
    path("", include(router.urls)),
]
