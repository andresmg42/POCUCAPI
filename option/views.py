from .models import Option
from rest_framework import viewsets, status, response
from .serailizer import OptionSerializer


class OptionViewSet(viewsets.ModelViewSet):

    queryset = Option.objects.all()
    serializer_class = OptionSerializer
