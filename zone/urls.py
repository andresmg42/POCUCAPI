from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views


router=DefaultRouter()
router.register(r'',views.ZoneViewSet,basename='visit')

urlpatterns = [
    path('get_zones_by_campus/',views.get_zones_by_campus,name='get_zones_by_campus'),
    path('',include(router.urls)),
    
]