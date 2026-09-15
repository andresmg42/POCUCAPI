from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from .user_utils import resolve_request_identity
from rest_framework import response,status,viewsets
from django.contrib.auth import get_user_model
from .user_utils import require_roles
from .permissions import UserPermissions
from .serializer import UserSerializer

User= get_user_model()


class UsersViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserPermissions]


@api_view(["GET"])
def get_role_status(request):
    identity = resolve_request_identity(request)

    return response.Response(
        {
            "is_authenticated": identity.is_authenticated,
            "is_admin": identity.is_admin,
            "is_observer": identity.is_observer,
            "is_staff":identity.is_staff
        },
        status=status.HTTP_200_OK,
    )

@api_view(["POST"])
@require_roles('admin')
def change_user_role(request):
    
    user_id=request.data.get('user_id')
    role=request.data.get('role')

    if not user_id or not role:
        response.Response({"message":"No user_id or role"},status=status.HTTP_400_BAD_REQUEST)

    user=get_object_or_404(User,id=user_id)

    if role=="staff":

        user.is_staff=True
        user.is_superuser=False
       
    elif role=="admin":
        user.is_staff=True
        user.is_superuser=True
        
    elif role=="observer":
        user.is_staff=False
        user.is_superuser=False

    else:
        return response.Response({"message":"invalid role"},status=status.HTTP_400_BAD_REQUEST)

    user.save(update_fields=['is_staff','is_superuser'])
    
    return response.Response({"message":"user role updated"},status=status.HTTP_200_OK)
