from rest_framework import viewsets, status, response
from .models import Question
from .serializer import (
    QuestionSerializerSimple,
    QuestionSerializer,
    QuestionSerializer2,
)
from rest_framework.decorators import api_view
from django.db import transaction
from django.db.models import F


class QuestionViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing survey sessions.
    This provides `list`, `create`, `retrieve`, `update`,
    and `destroy` actions automatically.
    """

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer2


@api_view(["GET"])
def get_question_by_survey(request):
    survey_id = request.GET.get("survey_id")

    if not survey_id:
        return response.Response(
            {"message": "survey_id is not valid"}, status=status.HTTP_404_NOT_FOUND
        )

    try:

        questions = list(
            Question.objects.filter(survey=survey_id, parent_question=None)
            .select_related("subcategory__category")
            .prefetch_related("options", "survey")
            .order_by("position")
        )
        all_questions = list(
            Question.objects.filter(survey=survey_id)
            .select_related("subcategory__category", "parent_question")
            .prefetch_related("options", "survey")
        )

        serializer = QuestionSerializer(
            questions, many=True, context={"all_questions": all_questions}
        )

        return response.Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return response.Response(
            {"message": "an unexpected error has occurred", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def get_questions_control_panel(request):
    survey_id = request.GET.get("survey_id")

    if not survey_id:
        return response.Response(
            {"message": "survey_id is not valid"}, status=status.HTTP_404_NOT_FOUND
        )
    try:
        questions = list(
            Question.objects.filter(survey=survey_id, parent_question=None)
            .select_related("subcategory__category")
            .prefetch_related("options", "survey")
            .order_by("position")
        )
        all_questions = list(
            Question.objects.filter(survey=survey_id)
            .select_related("subcategory__category", "parent_question")
            .prefetch_related("options", "survey")
        )

        serializer = QuestionSerializer(
            questions, many=True, context={"all_questions": all_questions}
        )

        grouped_data = {}
        for question_obj, question_data in zip(questions, serializer.data):
            category_name = None
            subcategory_name = None

            if question_obj.subcategory and question_obj.subcategory.category:
                category_name = question_obj.subcategory.category.name
            if question_obj.subcategory:
                subcategory_name = question_obj.subcategory.name

            if category_name is None:
                category_name = "Uncategorized"
            if subcategory_name is None:
                subcategory_name = "Uncategorized"

            grouped_data.setdefault(category_name, {})
            grouped_data[category_name].setdefault(subcategory_name, [])
            grouped_data[category_name][subcategory_name].append(question_data)

        return response.Response(grouped_data, status=status.HTTP_200_OK)

    except Exception as e:
        return response.Response(
            {"message": "an unexpected error has occurred", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['POST'])
def reorder_questions(request):
    new_questions=request.data

    if not new_questions:
        return response.Response({"message":"the array of questions is empty"},status=status.HTTP_400_BAD_REQUEST)
    
    for item in new_questions:
        if 'id' not in item or 'position' not in item:
            return response.Response({"message":"each question must include id and position fields"},status=status.HTTP_400_BAD_REQUEST)
        
    position_map={item['id']:item['position'] for item in new_questions}
    incoming_ids=list(position_map.keys())
    
    try:

        questions=list(Question.objects.filter(id__in=incoming_ids))

        if len(questions)!=len(incoming_ids):
            return response.Response({"message":"one or more questions ids were not found"},status=status.HTTP_404_NOT_FOUND)
    
    
        
        for question in questions:
            question.position=position_map[question.id]
        
        Question.objects.bulk_update(questions,fields=['position'])

    except Exception as e:
        return response.Response({"message":"an unexpected error acurred during bulkupdate","error":str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response.Response({"message":f"{len(questions)} Questions updated successfully"},status=status.HTTP_200_OK)

