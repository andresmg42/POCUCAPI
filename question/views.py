from rest_framework import viewsets,status,response
from .models import Question
from .serializer import QuestionSerializerSimple
from rest_framework.decorators import api_view


class QuestionViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing survey sessions.
    This provides `list`, `create`, `retrieve`, `update`,
    and `destroy` actions automatically.
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializerSimple


@api_view(['GET'])
def get_question_by_survey(request):
    survey_id=request.GET.get('survey_id')
    
    if not survey_id:
        return response.Response({'message':'survey_id is not valid'},satus=status.HTTP_404_NOT_FOUND)

    try:

        questions=Question.objects.filter(survey=survey_id, parent_question=None).distinct()

        serializer=QuestionSerializerSimple(questions,many=True)

        return response.Response(serializer.data,status=status.HTTP_200_OK)

    except Exception as e:
        return response.Response({'message':'an unexpected error has occurred','error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)   
        print(e)




