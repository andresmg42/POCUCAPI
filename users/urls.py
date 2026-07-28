from django.urls import path
from .views import get_role_status

urlpatterns=[
    path('get_role_status',get_role_status,name='get_role_status')
]