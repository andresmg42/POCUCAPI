from django.http import HttpResponse
from rest_framework.decorators import api_view
from category.models import Category
from category.serializer import CategorySerialier
from rest_framework.response import Response
from rest_framework import status,request


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@api_view(['GET'])
def get_categories(request):

    try:

        categories=Category.objects.all()
        serializer=CategorySerialier(categories,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error':str(e)})


