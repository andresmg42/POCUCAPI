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


@api_view(["POST"])
def create_or_update_batch_questions(request):
    data = request.data

    if not isinstance(data, list):
        return response.Response(
            {"message": "payload must be a list of questions"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    required_fields = ["code", "question_type", "description", "subcategory", "survey"]
    errors = []

    def normalize_item(item, parent_id_override=None):
        subcategory_value = item.get("subcategory")
        if isinstance(subcategory_value, dict):
            subcategory_id = subcategory_value.get("id")
        else:
            subcategory_id = subcategory_value

        parent_value = item.get("parent_question")
        if isinstance(parent_value, dict):
            parent_id = parent_value.get("id")
        else:
            parent_id = parent_value
        if parent_id_override is not None:
            parent_id = parent_id_override

        options_value = item.get("options") or []
        if options_value and isinstance(options_value[0], dict):
            options = [opt.get("id") for opt in options_value if opt.get("id")]
        else:
            options = options_value

        survey_value = item.get("survey") or []
        if survey_value and isinstance(survey_value[0], dict):
            survey = [surv.get("id") for surv in survey_value if surv.get("id")]
        else:
            survey = survey_value

        return {
            "id": item.get("id"),
            "subcategory_id": subcategory_id,
            "code": item.get("code"),
            "question_type": item.get("question_type"),
            "description": item.get("description"),
            "is_required": item.get("is_required", True),
            "input_type": item.get("input_type", Question.InputType.NUMERIC),
            "position": item.get("position", 1.0),
            "parent_question_id": parent_id,
            "options": options,
            "survey": survey,
        }

    parent_items = []
    children_by_parent_index = []

    for index, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append({"index": index, "error": "each item must be an object"})
            continue

        missing = [field for field in required_fields if item.get(field) in [None, ""]]
        if missing:
            errors.append({"index": index, "missing": missing})
            continue

        parent_items.append(item)
        children_by_parent_index.append(item.get("sub_questions") or [])

    if errors:
        return response.Response(
            {"message": "validation failed", "errors": errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        with transaction.atomic():
            to_create = []
            to_create_keys = []
            to_update_payload = {}
            update_ids = []

            for index, item in enumerate(parent_items):
                normalized = normalize_item(item)
                if normalized["id"]:
                    to_update_payload[normalized["id"]] = normalized
                    update_ids.append(normalized["id"])
                else:
                    to_create.append(
                        Question(
                            subcategory_id=normalized["subcategory_id"],
                            code=normalized["code"],
                            question_type=normalized["question_type"],
                            description=normalized["description"],
                            is_required=normalized["is_required"],
                            input_type=normalized["input_type"],
                            position=normalized["position"],
                            parent_question_id=normalized["parent_question_id"],
                        )
                    )
                    to_create_keys.append(index)

            updated_questions = []
            if update_ids:
                existing_questions = list(Question.objects.filter(id__in=update_ids))
                found_ids = {q.id for q in existing_questions}
                missing_ids = [
                    item_id for item_id in update_ids if item_id not in found_ids
                ]
                if missing_ids:
                    return response.Response(
                        {"message": "questions not found", "missing_ids": missing_ids},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                for question in existing_questions:
                    payload = to_update_payload.get(question.id, {})
                    question.subcategory_id = payload.get("subcategory_id")
                    question.code = payload.get("code")
                    question.question_type = payload.get("question_type")
                    question.description = payload.get("description")
                    question.is_required = payload.get("is_required")
                    question.input_type = payload.get("input_type")
                    question.position = payload.get("position")
                    question.parent_question_id = payload.get("parent_question_id")
                    updated_questions.append(question)

                Question.objects.bulk_update(
                    updated_questions,
                    [
                        "subcategory_id",
                        "code",
                        "question_type",
                        "description",
                        "is_required",
                        "input_type",
                        "position",
                        "parent_question_id",
                    ],
                )

            created_questions = Question.objects.bulk_create(to_create)
            created_by_index = {
                parent_index: question
                for parent_index, question in zip(to_create_keys, created_questions)
            }

            m2m_updates = []
            for index, item in enumerate(parent_items):
                normalized = normalize_item(item)
                question = None
                if normalized["id"]:
                    question = next(
                        (q for q in updated_questions if q.id == normalized["id"]), None
                    )
                if question is None:
                    question = created_by_index.get(index)
                if question is not None:
                    m2m_updates.append(
                        {
                            "question": question,
                            "options": normalized["options"],
                            "survey": normalized["survey"],
                        }
                    )

            child_to_create = []
            child_create_payloads = []
            child_to_update_payload = {}
            child_update_ids = []

            for parent_index, child_list in enumerate(children_by_parent_index):
                parent_question = created_by_index.get(parent_index)
                parent_id = parent_items[parent_index].get("id")
                if parent_question is not None:
                    parent_id = parent_question.id

                for child in child_list:
                    if not isinstance(child, dict):
                        continue
                    missing_child = [
                        field
                        for field in required_fields
                        if child.get(field) in [None, ""]
                    ]
                    if missing_child:
                        errors.append(
                            {
                                "index": parent_index,
                                "error": "child question missing fields",
                                "missing": missing_child,
                            }
                        )
                        continue
                    normalized_child = normalize_item(
                        child, parent_id_override=parent_id
                    )
                    if normalized_child["parent_question_id"] is None:
                        errors.append(
                            {
                                "index": parent_index,
                                "error": "child question missing parent_question",
                            }
                        )
                        continue

                    if normalized_child["id"]:
                        child_to_update_payload[normalized_child["id"]] = (
                            normalized_child
                        )
                        child_update_ids.append(normalized_child["id"])
                    else:
                        child_to_create.append(
                            Question(
                                subcategory_id=normalized_child["subcategory_id"],
                                code=normalized_child["code"],
                                question_type=normalized_child["question_type"],
                                description=normalized_child["description"],
                                is_required=normalized_child["is_required"],
                                input_type=normalized_child["input_type"],
                                position=normalized_child["position"],
                                parent_question_id=normalized_child[
                                    "parent_question_id"
                                ],
                            )
                        )
                        child_create_payloads.append(normalized_child)

            if errors:
                return response.Response(
                    {"message": "validation failed", "errors": errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            updated_children = []
            if child_update_ids:
                existing_children = list(
                    Question.objects.filter(id__in=child_update_ids)
                )
                found_child_ids = {q.id for q in existing_children}
                missing_child_ids = [
                    item_id
                    for item_id in child_update_ids
                    if item_id not in found_child_ids
                ]
                if missing_child_ids:
                    return response.Response(
                        {
                            "message": "questions not found",
                            "missing_ids": missing_child_ids,
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )

                for question in existing_children:
                    payload = child_to_update_payload.get(question.id, {})
                    question.subcategory_id = payload.get("subcategory_id")
                    question.code = payload.get("code")
                    question.question_type = payload.get("question_type")
                    question.description = payload.get("description")
                    question.is_required = payload.get("is_required")
                    question.input_type = payload.get("input_type")
                    question.position = payload.get("position")
                    question.parent_question_id = payload.get("parent_question_id")
                    updated_children.append(question)

                Question.objects.bulk_update(
                    updated_children,
                    [
                        "subcategory_id",
                        "code",
                        "question_type",
                        "description",
                        "is_required",
                        "input_type",
                        "position",
                        "parent_question_id",
                    ],
                )

            created_children = Question.objects.bulk_create(child_to_create)

            for question, payload in zip(created_children, child_create_payloads):
                m2m_updates.append(
                    {
                        "question": question,
                        "options": payload["options"],
                        "survey": payload["survey"],
                    }
                )

            for question in updated_children:
                payload = child_to_update_payload.get(question.id, {})
                m2m_updates.append(
                    {
                        "question": question,
                        "options": payload.get("options", []),
                        "survey": payload.get("survey", []),
                    }
                )

            for relation in m2m_updates:
                relation["question"].options.set(relation["options"] or [])
                relation["question"].survey.set(relation["survey"] or [])

        result_questions = (
            created_questions + updated_questions + created_children + updated_children
        )
        serializer = QuestionSerializerSimple(result_questions, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return response.Response(
            {"message": "an unexpected error has occurred", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT"])
def update_batch_questions(request):
    data = request.data

    if not isinstance(data, list):
        return response.Response(
            {"message": "payload must be a list of questions"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    errors = []
    payload_by_id = {}
    ids = []

    for index, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append({"index": index, "error": "each item must be an object"})
            continue

        item_id = item.get("id")
        if not item_id:
            errors.append({"index": index, "missing": ["id"]})
            continue

        payload_by_id[item_id] = item
        ids.append(item_id)

    if errors:
        return response.Response(
            {"message": "validation failed", "errors": errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        questions = list(Question.objects.filter(id__in=ids))
        if len(questions) != len(ids):
            found_ids = {q.id for q in questions}
            missing_ids = [item_id for item_id in ids if item_id not in found_ids]
            return response.Response(
                {"message": "questions not found", "missing_ids": missing_ids},
                status=status.HTTP_404_NOT_FOUND,
            )

        fields_to_update = [
            "subcategory_id",
            "code",
            "question_type",
            "description",
            "is_required",
            "input_type",
            "position",
            "parent_question_id",
        ]

        m2m_payload = []
        for question in questions:
            item = payload_by_id.get(question.id, {})

            if "subcategory" in item:
                question.subcategory_id = item.get("subcategory")
            if "code" in item:
                question.code = item.get("code")
            if "question_type" in item:
                question.question_type = item.get("question_type")
            if "description" in item:
                question.description = item.get("description")
            if "is_required" in item:
                question.is_required = item.get("is_required")
            if "input_type" in item:
                question.input_type = item.get("input_type")
            if "position" in item:
                question.position = item.get("position")
            if "parent_question" in item:
                question.parent_question_id = item.get("parent_question")

            m2m_payload.append(
                {
                    "question": question,
                    "options": item.get("options"),
                    "survey": item.get("survey"),
                }
            )

        with transaction.atomic():
            Question.objects.bulk_update(questions, fields_to_update)

            for relation in m2m_payload:
                if relation["options"] is not None:
                    relation["question"].options.set(relation["options"])
                if relation["survey"] is not None:
                    relation["question"].survey.set(relation["survey"])

        serializer = QuestionSerializerSimple(questions, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return response.Response(
            {"message": "an unexpected error has occurred", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
