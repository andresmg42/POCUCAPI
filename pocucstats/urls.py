from django.urls import path,include
from . import views


urlpatterns = [
    
    path("descriptive_analisis_by_question/", views.SurveyDashboardView.as_view(), name="descriptive_analisis_by_question"),

]