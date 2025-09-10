from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status,response
from .models import Surveysession
from .serializer import SurveysessionSerializer


def index(request):
    return HttpResponse("Hello, world. You're at the surveysession index.")

@api_view(['GET'])
def get_surveysession_by_id(request):

    data=request
    
    survey_s=Surveysession.objects.get(id=r)

