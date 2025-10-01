from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', views.CategoryViewSet, basename='category')

urlpatterns = [
    
    path("list/", views.get_categories, name="get_categories"),
    path("category_completed/", views.questions_of_category_completed, name="questions_of_category_completed"),
    path('', include(router.urls)),
]