from django.urls import path

from . import views

urlpatterns = [
    path("create/", views.create_response, name="create_response"),
    path('delete_responses_by_category/',views.delete_responses_by_category,name='delete_responses_by_category')
]