from django.shortcuts import render
from rest_framework.decorators import api_view
from .user_utils import resolve_request_identity
from rest_framework import response,status

@api_view(["GET"])
def get_role_status(request):
    identity = resolve_request_identity(request)

    return response.Response(
        {
            "is_authenticated": identity.is_authenticated,
            "is_admin": identity.is_admin,
            "is_observer": identity.is_observer,
        },
        status=status.HTTP_200_OK,
    )
