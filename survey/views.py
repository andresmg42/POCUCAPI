from django.http import HttpResponse
import requests
from rest_framework.decorators import api_view
from rest_framework import status,response
from observer.models import Observer
from observer.serializer import ObserverSerializer
from zone.models import Zone
from topic.models import Topic
from surveyversion.models import SurveyVersion
from .serializer import SurveySerializer
from .models import Survey

DATASURVEY={
  "marca temporal": "2025-09-05T22:04:09.000Z",
  "dirección de correo electrónico": "andresdavid.ortega@gmail.com",
  "zona": 1,
  "version encuesta": 1,
  "tema": "consumo de tabaco",
  "numero de encuesta": 1,
  "fecha de inicio": "2025-09-05T05:00:00.000Z",
  "fecha de finalizacion": "2025-09-05T05:00:00.000Z",
  "distancia de observacion (metros)": 12,
  "url carpeta drive de la evidencia fotografica": "https://docs.google.com/forms/d/e/1FAIpQLSdFZfLcqcxDXvR6-GORsRvkTV0NjNDLPYyTOuuzZOpD6nUoUg/viewform?usp=sharing&ouid=109351613319568914560"
}

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@api_view(['POST'])
def create_survey(request):
    data=request.data
    try:
        observer=Observer.objects.get(email=data['dirección de correo electrónico'])
        zone= Zone.objects.get(name=data['zona'])
        topic= Topic.objects.get(name=data['tema'])
        version_survey=SurveyVersion.objects.get(name=str(float(data[SurveyVersion])),topic=data['tema'])
    except Exception as e:
        print(e)


    newdata={
        "zone":zone.id,
        "observer":observer.id,
        "survey_version":version_survey.id,
        "url":data['url carpeta drive de la evidencia fotografica'],
        "survey_number":data['numero de encuesta'],
        "start_date":data['fecha de inicio'],
        "end_date":data['fecha de finalizacion'],
        "observational_distance":data['distancia de observacion (metros)']


    }

    serializer=SurveySerializer(data=newdata)
    if serializer.is_valid():

        validated_data=serializer.validated_data

        survey,created=Survey.objects.get_or_create()

    


    

    




