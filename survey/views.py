from django.http import HttpResponse
import requests
from rest_framework.decorators import api_view
from rest_framework import status,response
from .models import Survey
from .serializer import SurveySerializer
from question.models import Question, Question_Survey
from question.serializer import QuestionSerializer, QuestionSurveySerilizer


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@api_view(['GET'])
def list_surveys(request):

    surveys=Survey.objects.all()

    serializer= SurveySerializer(surveys,many=True)

    return response.Response(serializer.data,status=status.HTTP_200_OK)
    
@api_view(['GET'])
def get_questions_and_options(request):

    survey_id=request.GET.get('surveysession_id')

    print(survey_id)

    # if survey_id is 'undefined':
    #     return response.Response({'message':'id invalid in get_questions_and_options'},status=status.HTTP_400_BAS_REQUEST)
    
    # question_survey=Question_Survey.objects.filter(survey_id=survey_id)
    # print('survey_id',survey_id)}
    return response.Response({'message':'todo bien'})


