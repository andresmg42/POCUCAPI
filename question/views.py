from rest_framework import viewsets, status, response
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


@api_view(["GET"])
def get_question_by_survey(request):
    survey_id = request.GET.get("survey_id")

    if not survey_id:
        return response.Response(
            {"message": "survey_id is not valid"}, satus=status.HTTP_404_NOT_FOUND
        )

    try:

        questions = Question.objects.filter(
            survey=survey_id, parent_question=None
        ).distinct()

        serializer = QuestionSerializerSimple(questions, many=True)

        return response.Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return response.Response(
            {"message": "an unexpected error has occurred", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        

#this function was not implemented in the frontend but it can be usefult to future
# @api_view(["POST"])
# def create_new_child_question(request):
#     data = request.data

#     parent_question_id = data.get("parentId")
#     description = data.get("description")

#     if not parent_question_id or not description:
#         return response.Response(
#             {"message": "parentId and description are not valid"},
#             status=status.HTTP_400_BAD_REQUEST,
#         )
    
#     try:

#         parent_question = Question.objects.get(id=parent_question_id)
#     except Question.DoesNotExist:
#         return response.Response(
#             {"message": "Parent question not found."}, status=status.HTTP_404_NOT_FOUND
#         )
#     child_questions = Question.objects.filter(parent_question=parent_question)

#     new_number = 1
#     if child_questions.exists():
#         numbers = []
#         for q in child_questions:
#             try:
#                 number = q.code.split(sep=".")[-1]
#                 numbers.append(int(number))
#             except (ValueError, IndexError):
#                 pass

#         if numbers:
#             new_number = max(numbers)+1

#         new_question_dict = (
#             {
#                 "subcategory": parent_question.subcategory,
#                 "code": f"{parent_question.code}.{new_number}",
#                 "question_type": "matrix_child",
#                 "description": description,
#                 "is_required": parent_question.is_required,
#                 "parent_question": parent_question,
#                 "options": parent_question.options,
#                 "survey": parent_question.survey,
#             }
#         )

#         try:
#             new_question = Question.objects.create(**new_question_dict)

#             serializer = QuestionSerializerSimple(new_question)

#             return response.Response(
#                 {
#                     "message": "child question created successfully",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )

#         except Exception as e:

#             return response.Response(
#                 {"message": f"Error creating question: {e}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )
