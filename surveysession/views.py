from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status,response,viewsets
from .models import Surveysession
from .serializer import SurveysessionSerializer
from observer.models import Observer
from survey.models import Survey
from zone.models import Zone
from observer.models import Observer


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

# @api_view(['POST'])
# def create_survey_session(request):

#     data=request.data

#     print(data)
#     if not all(value!='' for value in data.values()):
#         return response.Response({'message':'some data value is empty'},status=status.HTTP_400_BAD_REQUEST)
#     try:

#         zone= Zone.objects.get(number=data['zone'])
#         observer=Observer.objects.get(email=data['email'])
#         survey=Survey.objects.get(id=data['survey_id'])

#         data['survey']=survey.id
#         data['zone']=zone.id
#         data['observer']=observer.id
        
        
#         print('data from fronted:',data)
#         serializer=SurveysessionSerializer(data=data)

#         if serializer.is_valid():

#             validated_data=serializer.validated_data

#             obj,created=Surveysession.objects.update_or_create(id=validated_data.session_id,default=validated_data)

#             if created:
#                 serializernew=SurveysessionSerializer(obj)
#                 return response.Response({'message':'new session created successfully','session':serializernew.data})
#             else:
#                 return response.Response({'message':'update surveysession succesfully'},status=status.HTTP_200_OK)
#         else:
#             return response.Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


#     except Exception as e:
#         return response.Response({'message':"error in create survey session",'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @api_view(['POST'])
# def create_survey_session(request):

#     data=request.data

#     print(data)
#     if not all(value!='' for value in data.values()):
#         return response.Response({'message':'some data value is empty'},status=status.HTTP_400_BAD_REQUEST)
#     try:

#         zone= Zone.objects.get(number=data['zone'])
#         observer=Observer.objects.get(email=data['email'])
#         survey=Survey.objects.get(id=data['survey_id'])

#         data['survey']=survey.id
#         data['zone']=zone.id
#         data['observer']=observer.id
        
#         print('data from fronted:',data)
#         serializer=SurveysessionSerializer(data=data)

#         if serializer.is_valid():

#             validated_data=serializer.validated_data

#             if 

#             if created:
#                 serializernew=SurveysessionSerializer(obj)
#                 return response.Response({'message':'new session created successfully','session':serializernew.data})
#             else:
#                 return response.Response({'message':'update surveysession succesfully'},status=status.HTTP_200_OK)
#         else:
#             return response.Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


#     except Exception as e:
#         return response.Response({'message':"error in create survey session",'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
   
# @api_view(['DELETE'])
# def delete_survey_session(request,pk):
#     try:
#         surveysession_obj=Surveysession.objects.get(id=pk)
#     except Surveysession.DoesNotExist:
#         return response.Response({'message':'the visit object do not exist'},status=status.HTTP_404_NOT_FOUND)  
#     surveysession_obj.delete()
   
#     return response.Response({'message':f'visit {pk} deleted'},status=status.HTTP_204_NO_CONTENT)


class SurveysessionViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing survey sessions.
    This provides `list`, `create`, `retrieve`, `update`,
    and `destroy` actions automatically.
    """
    queryset = Surveysession.objects.all().order_by('-uploaded_at')
    serializer_class = SurveysessionSerializer
