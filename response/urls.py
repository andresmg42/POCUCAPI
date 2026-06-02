from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"", views.ResponseViewSet, basename="response")

urlpatterns = [
    path("create/", views.create_response, name="create_response"),
    path(
        "delete_responses_by_category/",
        views.delete_responses_by_category,
        name="delete_responses_by_category",
    ),
    path("", include(router.urls)),
]
