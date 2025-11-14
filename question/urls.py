from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views


router=DefaultRouter()
router.register(r'',views.QuestionViewSet,basename='visit')

from . import views

urlpatterns = [
    path('get_questions_by_survey',views.get_question_by_survey,name='get_questions_by_survey'),
    # path('create_new_child_question',views.create_new_child_question,name='create_new_child_question'),

    path('',include(router.urls))
]

