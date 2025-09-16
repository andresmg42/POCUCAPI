from django.http import HttpResponse
import requests
from rest_framework.decorators import api_view
from rest_framework import status,response
from .models import Survey
from .serializer import SurveySerializer
from question.models import Question, Question_Survey
from question.serializer import QuestionSerializer, QuestionSurveySerilizer
from surveysession.models import Surveysession
from option.models import Option
from option.serailizer import OptionSerializer


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@api_view(['GET'])
def list_surveys(request):

    try:

        surveys=Survey.objects.all()

        serializer= SurveySerializer(surveys,many=True)

        return response.Response(serializer.data,status=status.HTTP_200_OK)
    
    except Exception as e:
        return response.Response({'message':'error in list_survey function','error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_questions_and_options(request):

    surveysession_id=request.GET.get('surveysession_id')

    resp=[]

    if surveysession_id in [None, 'undefined']:
        return response.Response({'message': 'id invalid in get_questions_and_options'}, 
                        status=status.HTTP_400_BAD_REQUEST)
    
    try:
        sessionsurvey=Surveysession.objects.get(id=surveysession_id)

        question_surveys=Question_Survey.objects.filter(survey=sessionsurvey.survey)

        for q_s in question_surveys:
            
            # new_question=Question.objects.get(id=q_s.question_id)
            questionserializer=QuestionSerializer(q_s.question)
            options=Option.objects.filter(question=q_s.question)
            q={'question':questionserializer.data,'options':[]}
            for option in options:           
                optionserializer=OptionSerializer(option)
                q['options'].append(optionserializer.data)
            
            resp.append(q)
        return response.Response(resp, status=status.HTTP_200_OK)
    
    except Surveysession.DoesNotExist:
        return response.Response({'error': 'Survey session not found'}, 
                        status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return response.Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
    


