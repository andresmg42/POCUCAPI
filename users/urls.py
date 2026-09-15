from django.urls import path,include
from . import views 
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"", views.UsersViewSet, basename="users")

urlpatterns=[
    path('get_role_status',views.get_role_status,name='get_role_status'),
    path('change_user_role',views.change_user_role,name='change_user_role'),
    path('',include(router.urls))
]
