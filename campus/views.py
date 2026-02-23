from rest_framework import viewsets
from .models import Campus
from .serializer import CampusSerializer

# Create your views here.
class CampusViewSet(viewsets.ModelViewSet):

    queryset= Campus.objects.all()
    serializer_class= CampusSerializer