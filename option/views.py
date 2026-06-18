from .models import Option
from rest_framework import viewsets, status, response
from .serailizer import OptionSerializer


class OptionViewSet(viewsets.ModelViewSet):

    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    def get_queryset(self):
        queryset=Option.objects.all()

        matching_type=self.request.query_params.get('matching_type')
        if matching_type:
            return queryset.filter(type=matching_type)
        return queryset
        
