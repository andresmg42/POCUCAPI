from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status, response, viewsets
from .models import Surveysession
from .serializer import SurveysessionSerializer
from observer.models import Observer
from survey.models import Survey
from zone.models import Zone
from observer.models import Observer
from django.utils import timezone
from .serializer import SessionReportSerializer
from users.user_utils import require_roles,filter_by_identity
from users.permissions import SurveySessionPermissions

@api_view(["GET"])
@require_roles("observer")
def get_surveysession_by_survey_id(request):

    id = request.GET.get("survey_id", None)


    try:

        if not id or id == "undefined":
            return response.Response(
                {"message": "survey_id invalid in get_surveysession_by_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        survey = Survey.objects.get(id=id)

        identity=request.identity

        if identity.is_observer:
            queryset=Surveysession.objects.filter(
                survey=survey,
                observer=identity.observer
            )
        
        serializer = SurveysessionSerializer(queryset, many=True)
    except Surveysession.DoesNotExist:
        return response.Response(
            {"message": "the survey session do not exists"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return response.Response(
            {
                "message": "an Error ocurred in get_survey_session_by_survey_id",
                "error": str(e),
            }
        )

    return response.Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@require_roles("observer")
def update_start_session(request):

    data = request.data

    session_id = data.get("surveysession_id")

    if not session_id:
        return response.Response(
            {"message": "session_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:

        session = Surveysession.objects.get(id=session_id, observer=request.identity.observer)

        if session.state == 0:
            session.state = 1
            session.start_date = timezone.now()
            session.save()

    except Surveysession.DoesNotExist:
        return response.Response(
            {"message": "surveysession object does not exists"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return response.Response(
            {"messge": "an unexpected error occurred in update_start_date"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response.Response(
        {"message": "session_start_date_time and state updated successfully"},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@require_roles("admin","staff")
def get_table_session_info(request):

    observer_id = request.GET.get("observer_id")
    survey_id = request.GET.get("survey_id")

    if not observer_id or not survey_id:
        return response.Respone(
            {"error": "the id observer query parameter is required."}
        )

    queryset = Surveysession.objects.filter(
        observer_id=observer_id, survey_id=survey_id
    )

    serializer_context = {
        "request": request,
    }

    serializer = SessionReportSerializer(
        queryset, many=True, context=serializer_context
    )

    return response.Response(serializer.data)


class SurveysessionViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing survey sessions.
    This provides `list`, `create`, `retrieve`, `update`,
    and `destroy` actions automatically.
    """

    queryset = Surveysession.objects.all().order_by("-uploaded_at")
    serializer_class = SurveysessionSerializer
    permission_classes=[SurveySessionPermissions]

    def get_queryset(self):

        identity=self.request.identity
        qs=Surveysession.objects.all()

        if identity.is_admin or identity.is_staff:
            return qs
        
        return qs.filter(observer=identity.observer)


    def perform_create(self,serializer):
        identity=self.request.identity

        if identity.is_observer and not (identity.is_admin or identity.is_staff):
            serializer.save(observer=identity.observer)
        else:
            serializer.save()
