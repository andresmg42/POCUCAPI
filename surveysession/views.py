from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status,response
from .models import Surveysession
from .serializer import SurveysessionSerializer
from observer.models import Observer
from survey.models import Survey
from zone.models import Zone
from observer.models import Observer

@api_view(['GET'])
def get_surveysession_by_id(request):

    id=request.GET.get('survey_id',None)
    email=request.GET.get('email',None)

    if id is 'undefined' or email is 'undefined':
        return response.Response({'message':'id or email invalid in get_surveysession_by_id'},status=status.HTTP_400_BAD_REQUEST)

    print('id:',id)
    print('email:',email)
 
    observer=Observer.objects.get(email=email)
    survey=Survey.objects.get(id=id)
    sessions= Surveysession.objects.filter(survey=survey,observer=observer)
    serializer=SurveysessionSerializer(sessions,many=True)


    return response.Response(serializer.data,status=status.HTTP_200_OK)

@api_view(['POST'])
def create_survey_session(request):

    data=request.data

    print(data)
    if not all(value!='' for value in data.values()):
        return response.Response({'message':'some data value is empty'},status=status.HTTP_400_BAD_REQUEST)
    try:

        zone= Zone.objects.get(number=data['zone'])
        observer=Observer.objects.get(email=data['email'])
        survey=Survey.objects.get(id=data['survey_id'])

        data['survey']=survey.id
        data['zone']=zone.id
        data['observer']=observer.id
        
        print('data from fronted:',data)
        serializer=SurveysessionSerializer(data=data)

        if serializer.is_valid():

            validated_data=serializer.validated_data

            obj,created=Surveysession.objects.get_or_create(**validated_data)

            if created:
                serializernew=SurveysessionSerializer(obj)
                return response.Response({'message':'new session created successfully','session':serializernew.data})
            else:
                return response.Response({'message':'this session already exists'})
        else:
            return response.Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


    except Exception as e:
        return response.Response({'message':"error in create survey session",'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
   

    



