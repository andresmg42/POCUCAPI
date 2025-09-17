from django.http import HttpResponse
from rest_framework.decorators import api_view
from category.models import Category
from rest_framework.response import Response
from rest_framework import status,request
from surveysession.models import Surveysession
from question.models import Question
from subcategory.models import Subcategory
from category.serializer import CategorySerializer
from question.serializer import QuestionSerializer


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@api_view(['GET'])
def get_categories(request):

    surveysession_id=request.GET.get('surveysession_id',None)
    
    if surveysession_id  in [None,'undefined']:
        return Response({'message':'invalid params id in get_categories'},status=status.HTTP_400_BAD_REQUEST)
    
    

    try:

        surveysession=Surveysession.objects.get(id=surveysession_id)
        survey=surveysession.survey
        questions=Question.objects.filter(survey=survey)

        categories=Category.objects.filter(subcategory__question__in=questions).distinct()

        res=CategorySerializer(categories,many=True)
        
        return Response(res.data,status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


