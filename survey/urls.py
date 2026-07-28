from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"surveys", views.SurveyViewSet, basename="survey")

urlpatterns = [
    path("list/", views.list_surveys, name="list_surveys"),
    path(
        "get_survey/", views.get_questions_and_options, name="get_questions_and_options"
    ),
    path("", include(router.urls)),
]
