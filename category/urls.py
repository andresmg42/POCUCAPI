from django.urls import path
from . import views

urlpatterns = [
    
    path("list/", views.get_categories, name="get_categories"),
    path("category_completed/", views.questions_of_category_completed, name="questions_of_category_completed"),
]