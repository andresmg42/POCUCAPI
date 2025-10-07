from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status,response,viewsets
from .models import Surveysession
from .serializer import SurveysessionSerializer
from observer.models import Observer
from survey.models import Survey
from zone.models import Zone
from observer.models import Observer
from django.utils import timezone


@api_view(['GET'])
def get_surveysession_by_survey_id(request):

    id=request.GET.get('survey_id',None)
    email=request.GET.get('email',None)

    print(email)
    print(id)
    try:

        if id == 'undefined' or email == 'undefined':
            return response.Response({'message':'id or email invalid in get_surveysession_by_id'},status=status.HTTP_400_BAD_REQUEST)

        observer=Observer.objects.get(email=email)
        survey=Survey.objects.get(id=id)
        sessions= Surveysession.objects.filter(survey=survey,observer=observer)
        serializer=SurveysessionSerializer(sessions,many=True)
    except Surveysession.DoesNotExist:
        return response.Response({'message':'the survey session do not exists'},status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return response.Response({'message':'an Error ocurred in get_survey_session_by_survey_id','error':str(e)})

    return response.Response(serializer.data,status=status.HTTP_200_OK)


@api_view(['POST'])
def update_start_session(request):

    data=request.data

    session_id=data.get('surveysession_id')

    if not session_id:
        return response.Response({'message': 'session_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:

        session=Surveysession.objects.get(id=session_id)

        if session.state==0:
            session.state=1
            session.start_date=timezone.now()
            session.save()


    except Surveysession.DoesNotExist:
        return response.Response({'message':'surveysession object does not exists'},status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return response.Response({'messge':'an unexpected error occurred in update_start_date'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response.Response({'message':'session_start_date_time and state updated successfully'},status=status.HTTP_200_OK)


# @api_view(['POST'])
# def update_start_date(request):

#     data=request.data

#     session_id=data['survesession_id']

#     if not session_id:
#         return response.Response({'message': 'surveysession_id is required'}, status=status.HTTP_400_BAD_REQUEST)

#     try:

#         session=Surveysession.objects.get(id=session_id)

#         if session.state==0:
#             session.state=1
#             session.start_date=timezone.now()
#             session.save()


#     except Surveysession.DoesNotExist:
#         return response.Response({'message':'surveysession object does not exists'},status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return response.Response({'messge':'an unexpected error occurred in update_start_date'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     return response.Response({'message':'start_date and state updated successfully in surveysession'},status=status.HTTP_200_OK)


class SurveysessionViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing survey sessions.
    This provides `list`, `create`, `retrieve`, `update`,
    and `destroy` actions automatically.
    """
    queryset = Surveysession.objects.all().order_by('-uploaded_at')
    serializer_class = SurveysessionSerializer
