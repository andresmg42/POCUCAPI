from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"", views.QuestionViewSet, basename="visit")

from . import views

urlpatterns = [
    path(
        "get_questions_by_survey",
        views.get_question_by_survey,
        name="get_questions_by_survey",
    ),
    # path(
    #     "get_questions_by_survey_cpanel",
    #     views.get_questions_control_panel,
    #     name="get_questions_control_panel",
    # ),
    path(
        "reorder_questions",
        views.reorder_questions,
        name="reorder_questions",
    ),
    path(
        "get_questions_bank",
        views.get_questions_bank,
        name="get_questions_bank"
    ),
    path("", include(router.urls)),
]
