from rest_framework import viewsets, status, response
from .models import Subcategory
from .serializer import SubcategorySerializer
from rest_framework.decorators import api_view


class SubcategoryViewSet(viewsets.ModelViewSet):

    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer
