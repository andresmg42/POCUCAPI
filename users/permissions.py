# users/permissions.py
from rest_framework.permissions import BasePermission
from .user_utils import resolve_request_identity


class RoleBasedPermission(BasePermission):
    """
    Subclass and define `action_roles`, mapping DRF action names to
    the set of roles allowed to perform them.
    """

    action_roles = {
        "list": ["admin", "staff", "observer"],
        "retrieve": ["admin", "staff", "observer"],
        "create": ["admin", "staff"],
        "update": ["admin", "staff"],
        "partial_update": ["admin", "staff"],
        "destroy": ["admin"],
    }  

    def has_permission(self, request, view):
        identity = resolve_request_identity(request)
        request.identity = identity

        if not identity.is_authenticated:
            return False

        allowed_roles = self.action_roles.get(view.action, [])
        print('action',view.action)
        print(allowed_roles)
        print('identity is admin',identity.is_admin)
        return identity.role in allowed_roles


class QuestionPermission(RoleBasedPermission):
    pass


class CampusPermission(RoleBasedPermission):
    pass

class ZonePermission(RoleBasedPermission):
    pass


class CategoryPermission(RoleBasedPermission):
    pass


class ObserverPermission(RoleBasedPermission):
    pass

class OptionPermissions(RoleBasedPermission):
    pass

class ResponsePermissions(RoleBasedPermission):
    action_roles = {
        "list": ["admin", "staff"],
        "retrieve": ["admin", "staff"],
        "create": ["admin", "staff","observer"],
        "update": ["admin"],
        "partial_update": ["admin"],
        "destroy": ["admin"],
    }

class SubcategoryPermissions(RoleBasedPermission):
    pass

class SurveyPermissions(RoleBasedPermission):
    pass

class SurveySessionPermissions(RoleBasedPermission):
    action_roles = {
        "list": ["admin", "staff","observer"],
        "retrieve": ["admin", "staff","observer"],
        "create": ["admin", "staff", "observer"],
        "update": ["admin","staff","observer"],
        "partial_update": ["admin","staff","observer"],
        "destroy": ["admin","staff","observer"],
    }

    def has_object_permission(self, request, view, obj):
        identity= resolve_request_identity(request)
        if identity.is_admin:
            return True
        
        if identity.is_staff:
            return view.action != 'destroy'
        
        return obj.observer == identity.observer
