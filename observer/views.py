from django.http import HttpResponse
import requests
from rest_framework.decorators import api_view
from rest_framework import status,response
from .models import Observer
from .serializer import ObserverSerializer
from surveysession.models import Surveysession
from .serializer import ObserverTableSerializer
from django.db.models import Count,Q

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@api_view(['POST'])
def registre_obsever(request):

    data=request.data

    print(data)
    
    serializer=ObserverSerializer(data=data)
    if serializer.is_valid():

        validated_data=serializer.validated_data
        
        observer,created=Observer.objects.get_or_create(email=validated_data['email'],defaults=validated_data)

        observer_serializer=ObserverSerializer(observer)

        if  not created:
            observer.name=validated_data['name']
            print("observer whit this email already exists")
            return response.Response({'message':'observer whit this email already exists',"user":observer_serializer.data})
        else:
            print("observer was created successfully ")
        
    else:
        print("user not valid")
        return response.Response({"message":"user not valid"},status=status.HTTP_400_BAD_REQUEST)

    return response.Response({"message":"user created or updated succesfully","user":observer_serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_table_observer_info(request):

    survey_id=request.GET.get('survey_id')

    if not survey_id:

        return response.Response({'message':'the survey_id is undefined'},status=status.HTTP_400_BAD_REQUEST)

    try:

        observers=Observer.objects.annotate(
            total_sessions=Count('surveysessions',filter=Q(surveysessions__survey_id=survey_id)),
            completed_sessions=Count('surveysessions',filter=Q(surveysessions__state=2, surveysessions__survey_id=survey_id))
        ).filter(total_sessions__gt=0).order_by('-register_date')

        serializer= ObserverTableSerializer(observers,many=True)

        return response.Response({'data':serializer.data},status=status.HTTP_200_OK)

    except Exception as e:
        return response.Response({'message':'An unexpected error occurred','error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# @api_view(['GET'])
# def get_table_observer_info(request):
    
#     items_list=[]

#     try:

#         observers= Observer.objects.all()



#         for observer in observers:

#             completed_sessions=Surveysession.objects.filter(observer=observer,state=2).count()

#             total_sessions=Surveysession.objects.filter(observer=observer).count()

#             string_sessions= f'{completed_sessions}/{total_sessions}'

#             completed_rate=0

#             if total_sessions>0:
#                 completed_rate=(completed_sessions/total_sessions)*100


#             new_observer={
#                 "id":observer.id,
#                 "email":observer.email,
#                 "sessions":string_sessions,
#                 "completed_rate":completed_rate,
#                 "register_date":observer.register_date

#             }

#             items_list.append(new_observer)
        
#         return response.Response({'data':items_list},status=status.HTTP_200_OK)
#     except Observer.DoesNotExist:
#         return response.Response({'message':'the observer do not exists'},status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return response.Response({'message':'an unexpected error ocurred in get table observer info','error':str(e)})

    





