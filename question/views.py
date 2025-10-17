from django.http import HttpResponse
from rest_framework import viewsets
from .models import Question
from .serializer import QuestionSerializerSimple


class QuestionViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing survey sessions.
    This provides `list`, `create`, `retrieve`, `update`,
    and `destroy` actions automatically.
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializerSimple