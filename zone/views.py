from rest_framework import viewsets,status,response
from .models import Zone
from .serializer import ZoneSerializer
from rest_framework.decorators import api_view


class ZoneViewSet(viewsets.ModelViewSet):
   
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer

@api_view(["GET"])
def get_zones_by_campus(request):
   
    campus_id = request.GET.get("campus_id")

    
    if not campus_id:
        return response.Response(
            {"message": "campus_id parameter is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
       
        zones = Zone.objects.filter(campus_id=campus_id)
        
        
        serializer = ZoneSerializer(zones, many=True)

        
        return response.Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return response.Response(
            {"message": "An unexpected error occurred", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )