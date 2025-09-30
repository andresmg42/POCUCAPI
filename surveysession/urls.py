from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router specifically for this app
router = DefaultRouter()
router.register(r'', views.SurveysessionViewSet, basename='surveysession')

# The app's URL patterns
urlpatterns = [
    path('get_survey_session_by_survey_id', views.get_surveysession_by_survey_id,name='get_surveysession_by_id'),
    path('', include(router.urls)),
]