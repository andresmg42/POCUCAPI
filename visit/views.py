from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework import status,response
from .models import Visit
from .serializer import VisitSerializer
from surveysession.models import Surveysession


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@api_view(['GET'])
def get_visits_by_id_session(request):

    id_surveysession=request.GET.get('surveysession_id',None)

    print('id surveysession: ',id_surveysession)
    

    if id_surveysession is 'undefined':
        return response.Response({'message':'id invalid in get_visits_by_id_session'},status=status.HTTP_400_BAD_REQUEST)

    surveysession=Surveysession.objects.get(id=id_surveysession)
    
    visits= Visit.objects.filter(surveysession=surveysession)
    serializer=VisitSerializer(visits,many=True)


    return response.Response(serializer.data,status=status.HTTP_200_OK)
    

@api_view(['POST'])
def create_visit(request):

    data=request.data

    print(data)

    if not all(value!='' for value in data.values()):
        return response.Response({'message':'some data is empty'},status=status.HTTP_400_BAD_REQUEST)
    
    try:

        serializer=VisitSerializer(data=data)

        if serializer.is_valid():
            
            validated_data=serializer.validated_data
            obj,created=Visit.objects.get_or_create(**validated_data)

            if created:
                serializernew=VisitSerializer(obj)
                return response.Response({'message':'new visit created successfully','session':serializernew.data},status=status.HTTP_200_OK)
            else:
                return response.Response({'message':'this visit already exists'})
        else:
            return response.Response(serializer.erros,status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:

        return response.Response({'message':'error in create visit','error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



