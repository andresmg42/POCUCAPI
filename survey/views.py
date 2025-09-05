from django.http import HttpResponse
import requests
from rest_framework.decorators import api_view
from rest_framework import status,response
from observer.models import Observer


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@api_view(['POST'])
def resiveResponses(request):
    print(request.data)
    return response.Response({"message":"todo bien"}, status=status.HTTP_200_OK)

    