# users/permissions.py
from rest_framework.permissions import BasePermission
from .user_utils import resolve_request_identity


class IsAdminOrObserver(BasePermission):
    allowed_roles = ("admin", "observer")

    def has_permission(self, request, view):
        identity = resolve_request_identity(request)
        request.identity = identity

        if "admin" in self.allowed_roles and identity.is_admin:
            return True
        if "observer" in self.allowed_roles and identity.is_observer:
            return True
        return False


class IsAdminOnly(IsAdminOrObserver):
    allowed_roles = ("admin",)
