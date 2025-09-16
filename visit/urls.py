from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("sessionvisits/", views.get_visits_by_id_session, name="get_visits_by_id_session"),
    path("create/", views.create_visit, name="create_visit"),

]