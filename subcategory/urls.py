from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"", views.SubcategoryViewSet, basename="subcategory")

urlpatterns = [
    path("", include(router.urls)),
]
