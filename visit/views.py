from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework import status,response,viewsets
from .models import Visit
from .serializer import VisitSerializer
from surveysession.models import Surveysession
from django.utils import  timezone
from response.models import Response

@api_view(['GET'])
def get_visits_by_id_session(request):

    id_surveysession=request.GET.get('surveysession_id',None)

    print('id surveysession: ',id_surveysession)
    

    if id_surveysession in  ['undefined',None]:
        return response.Response({'message':'id invalid in get_visits_by_id_session'},status=status.HTTP_400_BAD_REQUEST)

    surveysession=Surveysession.objects.get(id=id_surveysession)
    
    visits= Visit.objects.filter(surveysession=surveysession).order_by('visit_number')
    serializer=VisitSerializer(visits,many=True)


    return response.Response(serializer.data,status=status.HTTP_200_OK)

@api_view(['POST'])
def update_start_date(request):

    data=request.data

    visit_id=data['visit_id']

    if not visit_id:
        return response.Response({'message': 'visit_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:

        visit=Visit.objects.get(id=visit_id)

        if visit.state==0:
            visit.state=1
            visit.visit_start_date_time=timezone.now()
            visit.save()


    except Visit.DoesNotExist:
        return response.Response({'message':'visit object does not exists'},status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return response.Response({'messge':'an unexpected error occurred in update_start_date'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response.Response({'message':'visit_start_date_time and state updated successfully'},status=status.HTTP_200_OK)

    

class VisitViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing survey sessions.
    This provides `list`, `create`, `retrieve`, `update`,
    and `destroy` actions automatically.
    """
    queryset = Visit.objects.all().order_by('visit_number')
    serializer_class = VisitSerializer

    

