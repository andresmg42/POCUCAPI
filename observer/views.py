from django.http import HttpResponse
import requests
from rest_framework.decorators import api_view
from rest_framework import status, response, viewsets
from .models import Observer
from .serializer import ObserverSerializer
from surveysession.models import Surveysession
from .serializer import ObserverTableSerializer
from django.db.models import Count, Q


class ObserverViewSet(viewsets.ModelViewSet):

    queryset = Observer.objects.all()
    serializer_class = ObserverSerializer


@api_view(["POST"])
def registre_obsever(request):

    data = request.data

    print(data)

    serializer = ObserverSerializer(data=data)
    if serializer.is_valid():

        validated_data = serializer.validated_data

        observer, created = Observer.objects.get_or_create(
            email=validated_data["email"], defaults=validated_data
        )

        observer_serializer = ObserverSerializer(observer)

        if not created:
            observer.name = validated_data["name"]
            print("observer whit this email already exists")
            return response.Response(
                {
                    "message": "observer whit this email already exists",
                    "user": observer_serializer.data,
                }
            )
        else:
            print("observer was created successfully ")

    else:
        print("user not valid")
        return response.Response(
            {"message": "user not valid"}, status=status.HTTP_400_BAD_REQUEST
        )

    return response.Response(
        {
            "message": "user created or updated succesfully",
            "user": observer_serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def get_table_observer_info(request):

    survey_id = request.GET.get("survey_id")

    if not survey_id:

        return response.Response(
            {"message": "the survey_id is undefined"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:

        observers = (
            Observer.objects.annotate(
                total_sessions=Count(
                    "surveysessions", filter=Q(surveysessions__survey_id=survey_id)
                ),
                completed_sessions=Count(
                    "surveysessions",
                    filter=Q(
                        surveysessions__state=2, surveysessions__survey_id=survey_id
                    ),
                ),
            )
            .filter(total_sessions__gt=0)
            .order_by("-register_date")
        )

        serializer = ObserverTableSerializer(observers, many=True)

        return response.Response({"data": serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return response.Response(
            {"message": "An unexpected error occurred", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
