from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.registre_obsever, name="registreObserver"),
    path("get_table_observer_info/", views.get_table_observer_info, name="get_table_observer_info"),
    
]