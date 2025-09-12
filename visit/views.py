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
    # return response.Response({'message':'all good'},status=status.HTTP_200_OK)