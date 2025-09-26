from django.urls import path
from . import views

urlpatterns = [
    
    path("get_survey_session_by_id/", views.get_surveysession_by_id, name="get_survey_session_by_id"),
    path("create/", views.create_survey_session, name="create_survey_session"),
    path("delete/<int:pk>", views.delete_survey_session, name="delete_survey_session"),
]