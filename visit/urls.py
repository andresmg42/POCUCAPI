from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views

router=DefaultRouter()
router.register(r'',views.VisitViewSet,basename='visit')

urlpatterns = [
    path("sessionvisits/", views.get_visits_by_id_session, name="get_visits_by_id_session"),
    path('',include(router.urls))
]