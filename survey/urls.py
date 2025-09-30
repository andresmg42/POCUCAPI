from django.urls import path

from . import views

urlpatterns = [
    path("list/", views.list_surveys, name="list_surveys"),
    path("get_survey/", views.get_questions_and_options, name="get_questions_and_options"),
]