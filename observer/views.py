from django.http import HttpResponse
import requests
from rest_framework.decorators import api_view
from rest_framework import status,response
from .models import Observer
from .serializer import ObserverSerializer

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@api_view(['POST'])
def registre_obsever(request):

    data=request.data
    newdata={
        'name':data['nombre'],
        'email':data['dirección de correo electrónico'],
        'telephone':data['telefono']
    }

    serializer=ObserverSerializer(data=newdata)
    if serializer.is_valid():

        validated_data=serializer.validated_data
        
        observer,created=Observer.objects.get_or_create(email=validated_data['email'],defaults=validated_data)

        if  not created:
            observer.name=validated_data['name']
            observer.telephone=validated_data['telephone']
            print("observer whit this email already exists")
            return response.Response({'message':'observer whit this email already exists'})
        else:
            print("observer was created successfully ")
        
    else:
        print("user not valid")

    return response.Response({"message":"user created or updated succesfully"}, status=status.HTTP_200_OK)