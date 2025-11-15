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
from question.serializer import QuestionSerializer2

from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import firebase_admin
from firebase_admin import credentials, auth
import os

FIREBASE_KEY_PATH=os.environ.get('FIREBASE_KEY_PATH','pocuc/firebase_key.json')

cred = credentials.Certificate(FIREBASE_KEY_PATH)
firebase_admin.initialize_app(cred)



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

    if surveysession_id  in [None, 'undefined'] and category_id in [None, 'undefined'] :
        return response.Response({'message': 'id invalid in get_questions_and_options'}, 
                        status=status.HTTP_400_BAD_REQUEST)
    
    try:
        sessionsurvey=Surveysession.objects.get(id=surveysession_id)

        category= Category.objects.get(id=category_id)
        
        all_questions= Question.objects.filter(
            survey=sessionsurvey.survey,
            subcategory__in=category.subcategory_set.all()
        ).prefetch_related('options').order_by('position')


        top_level_questions=[q for q in all_questions if q.parent_question is None]
        
        context={'all_questions': all_questions}

        serializer=QuestionSerializer(top_level_questions,many=True,context=context)
            
        return response.Response(serializer.data, status=status.HTTP_200_OK)
    
    except Surveysession.DoesNotExist:
        return response.Response({'error': 'Survey session not found'}, 
                        status=status.HTTP_404_NOT_FOUND)
    
    except Category.DoesNotExist:
        return response.Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return response.Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)  

class CheckAdminStatus(APIView):
    def post(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "Authorization header missing or malformed"}, status=status.HTTP_401_UNAUTHORIZED)

        id_token = auth_header.split(' ')[1]

        try:
            
            decoded_token = auth.verify_id_token(id_token)
            user_email = decoded_token['email']

           
            try:
                user = User.objects.get(email=user_email)
                if user.is_staff or user.is_superuser:
                    return Response({"isAdmin": True, "message": "Access granted."}, status=status.HTTP_200_OK)
                else:
                    return Response({"isAdmin": False, "message": "User is not an admin."}, status=status.HTTP_403_FORBIDDEN)
            except User.DoesNotExist:
                return Response({"error": "User with this email not found."}, status=status.HTTP_404_NOT_FOUND)

        except auth.InvalidIdTokenError:
            return Response({"error": "Invalid Firebase ID token"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
