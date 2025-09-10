from django.http import HttpResponse
import requests
from rest_framework.decorators import api_view
from rest_framework import status,response
from .models import Survey
from .serializer import SurveySerializer


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@api_view(['GET'])
def list_surveys(request):

    surveys=Survey.objects.all()

    serializer= SurveySerializer(surveys,many=True)

    return response.Response(serializer.data,status=status.HTTP_200_OK)
    


