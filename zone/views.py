from rest_framework import viewsets
from .models import Zone
from .serializer import ZoneSerializer


class ZoneViewSet(viewsets.ModelViewSet):
   
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer

