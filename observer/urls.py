from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"", views.ObserverViewSet, basename="observer")

urlpatterns = [
    path("create/", views.registre_obsever, name="registreObserver"),
    path(
        "get_table_observer_info/",
        views.get_table_observer_info,
        name="get_table_observer_info",
    ),
    path("", include(router.urls)),
]
