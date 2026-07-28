from django.http import HttpResponse
from rest_framework import status, response, viewsets
from rest_framework.decorators import api_view
from .serializer import ResponseSerializer
from .models import Response, QuestionCommentAnswer
from surveysession.models import Surveysession
from survey.models import Survey
from visit.models import Visit
from question.models import Question
from datetime import datetime
from django.utils import timezone
from .models import QuestionCommentAnswer
from .serializer import QuestionCommentAnswerSerializer
from rest_framework.exceptions import ValidationError
from zone.models import Zone
from users.permissions import ResponsePermissions
from users.user_utils import require_roles
class ResponseViewSet(viewsets.ModelViewSet):

    queryset = Response.objects.all()
    serializer_class = ResponseSerializer
    permission_classes=[ResponsePermissions]


@api_view(["POST"])
@require_roles('observer','admin','staff')
def create_response(request):
    data = request.data

    print(data)

    response_data = data.get("answers", {})
    comments_data = data.get("comments", {})

    responses = []
    raw_responses = []

    try:

        if not response_data:
            return response.Response(
                {"message": "requested body can not be empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for question_id, answer in response_data.items():
            new_res = {
                "question": question_id,
                "option": answer.get("optionId"),
                "visita": answer.get("visitId"),
                "numeric_value": answer.get("numeric_value"),
                "text_value": answer.get("textValue"),
            }
            raw_responses.append(new_res)

        visit_id = raw_responses[0]["visita"]

        serializer = ResponseSerializer(data=raw_responses, many=True)

        if serializer.is_valid():

            validated_data = serializer.validated_data

            updated_session = False

            objects_to_create = [Response(**data) for data in validated_data]

            Response.objects.bulk_create(objects_to_create, ignore_conflicts=True)

            store_response_comments(comments_data)

            if validate_visit_is_completed(validated_data, visit_id):

                Visit.objects.filter(id=visit_id).update(
                    state=2, visit_end_date_time=timezone.now()
                )

                updated_session = validate_and_update_surveysession_state(visit_id)

            return response.Response(
                {
                    "message": "Responses created successfully",
                    "session_completed": updated_session,
                },
                status=status.HTTP_201_CREATED,
            )

        else:
            return response.Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
    except (ValueError, TypeError) as e:
        return response.Response(
            {"message": "Invalid numeric value provided.", "error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as e:
        return response.Response(
            {"message": "error in crate response", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def validate_visit_is_completed(data, visit_id):
    # 1. Validación básica
    if not visit_id:
        return False

    try:
        # Usamos select_related para optimizar la carga de datos relacionados
        visit = Visit.objects.select_related(
            "surveysession__zone", "surveysession__survey"
        ).get(id=visit_id)
        zone = visit.surveysession.zone
        survey = visit.surveysession.survey

        # 2. Definir lógica de tipos de zona (Tu matriz de permisos)
        allowed_types = [zone.zone_type, None]
        if zone.zone_type == Zone.ZoneType.MIXED:
            allowed_types.extend([Zone.ZoneType.OPEN, Zone.ZoneType.CLOSED])

        # 3. Obtener IDs de preguntas REQUERIDAS
        # GRACIAS A TU RELATED_NAME='questions', podemos acceder directo desde 'survey':
        required_questions_ids = set(
            survey.questions.filter(
                is_required=True,
                subcategory__category__target_zone_type__in=allowed_types,
            )
            .exclude(question_type="matrix_parent")
            .values_list("id", flat=True)
        )

    except Visit.DoesNotExist:
        return False

    # 4. Recopilar IDs de las respuestas que vienen en 'data' (lo nuevo)
    new_answers_ids = set()
    if data:
        for response_item in data:
            # Asumiendo que 'data' ya fue validada por el Serializer
            question_obj = response_item.get("question")
            if question_obj:
                new_answers_ids.add(question_obj.id)

    # 5. Recopilar IDs de las respuestas YA guardadas en BD (lo viejo)
    # Importante: Verifica si el campo en tu modelo Response es 'visit' o 'visita'
    db_answers_ids = set(
        Response.objects.filter(
            visita=visit_id  # Ajusta este nombre si tu campo es 'visit'
        ).values_list("question_id", flat=True)
    )

    # 6. Unir ambos conjuntos de respuestas
    all_answered_ids = new_answers_ids.union(db_answers_ids)

    # 7. Comprobar si los Requeridos son un subconjunto de los Respondidos
    # Retorna True solo si faltan 0 preguntas obligatorias
    return required_questions_ids.issubset(all_answered_ids)


def validate_and_update_surveysession_state(visit_id):
    try:

        session = Surveysession.objects.get(visits__id=visit_id)

        print("session_id", session.number_session)

        completed_visits = session.visits.filter(state=2)

        if session.visit_number == completed_visits.count():
            session.state = 2
            session.end_date = timezone.now()
            session.save()
            print(f"Session {session.id} updated successfully.")
            return True

        else:
            session.state = 1
            session.end_date = None
            session.save()
            return False

    except Surveysession.DoesNotExist:
        print(f"Error: No Surveysession found for visit_id {visit_id}")
        return False
    except Exception as e:
        print(f"error:", str(e))
        return False


@api_view(["DELETE"])
@require_roles('admin','observer','staff')
def delete_responses_by_category(request):

    visit_id = request.query_params.get("visit_id")
    category_id = request.query_params.get("category_id")

    if visit_id in ["undefined", None] or category_id in ["undefined", None]:
        return response.Response(
            {"message": "visit_id or category_id empty"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:

        delete_count, _ = Response.objects.filter(
            question__subcategory__category_id=category_id, visita=visit_id
        ).delete()
        delete_comments_count, _ = QuestionCommentAnswer.objects.filter(
            question__subcategory__category_id=category_id, visita=visit_id
        ).delete()

        if delete_count > 0:
            visit = Visit.objects.get(id=visit_id)
            visit.visit_end_date_time = None
            visit.state = 1
            visit.save()
            validate_and_update_surveysession_state(visit_id)
            return response.Response(
                {"message": f"{delete_count} response deleted"},
                status=status.HTTP_200_OK,
            )

        else:
            return response.Response(
                {"message": "there is not responses to delete"},
                status=status.HTTP_404_NOT_FOUND,
            )
    except Visit.DoesNotExist:
        return response.Response(
            {"message": "visit not found"}, status=status.HTTP_404_NOT_FOUND
        )

    except Exception as e:
        return response.Response(
            {"message": "error in delete_questions_by_category", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def store_response_comments(comments):

    raw_comments = []

    for question_id, comment in comments.items():
        if comment:
            new_res = {
                "question": question_id,
                "visita": comment.get("visitId"),
                "comment": comment.get("comment"),
            }
            raw_comments.append(new_res)

    if not raw_comments:
        return

    serializer = QuestionCommentAnswerSerializer(data=raw_comments, many=True)

    if not serializer.is_valid():

        raise ValidationError(serializer.errors)

    objects_to_create = [
        QuestionCommentAnswer(**data) for data in serializer.validated_data
    ]

    QuestionCommentAnswer.objects.bulk_create(objects_to_create, ignore_conflicts=True)
