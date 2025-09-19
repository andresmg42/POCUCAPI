from django.http import HttpResponse
import requests
from rest_framework.decorators import api_view
from rest_framework import status,response
from .models import Survey
from .serializer import SurveySerializer
from question.models import Question
from question.serializer import QuestionSerializer
from surveysession.models import Surveysession
from option.models import Option
from option.serailizer import OptionSerializer
from category.models import Category
from subcategory.models import Subcategory


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
    category_id=request.GET.get('category_id')

    resp=[]

    if surveysession_id  in [None, 'undefined'] and category_id in [None, 'undefined'] :
        return response.Response({'message': 'id invalid in get_questions_and_options'}, 
                        status=status.HTTP_400_BAD_REQUEST)
    
    try:
        sessionsurvey=Surveysession.objects.get(id=surveysession_id)

        category= Category.objects.get(id=category_id)
        
        subcategories=category.subcategory_set.all()
        survey=sessionsurvey.survey

        questions=Question.objects.filter(survey=survey,subcategory__in=subcategories)

        for question in questions:

            questionserializer=QuestionSerializer(question)
            options=Option.objects.filter(question=question)
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
                    
    


