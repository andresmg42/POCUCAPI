from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views


router=DefaultRouter()
router.register(r'',views.QuestionViewSet,basename='visit')

from . import views

urlpatterns = [
    path('',include(router.urls))
]