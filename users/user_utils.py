from firebase_admin import auth as firebase_auth
from django.contrib.auth import get_user_model
from observer.models import Observer
from functools import wraps
from rest_framework import response
User = get_user_model()


class AuthResult:
    def __init__(self, django_user=None, observer=None):
        self.django_user = django_user
        self.observer = observer

    @property
    def is_admin(self):
        return self.django_user is not None and self.django_user.is_superuser

    @property
    def is_staff(self):
        return (
            self.django_user is not None
            and self.django_user.is_staff
            and not self.django_user.is_superuser
        )

    @property
    def is_observer(self):
        return self.observer is not None
    
    
    @property
    def is_authenticated(self):
        return self.django_user is not None or self.observer is not None

    @property
    def role(self):
        if self.is_admin:
            return "admin"
        if self.is_staff:
            return "staff"
        if self.is_observer:
            return "observer"
        return None


def resolve_request_identity(request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return AuthResult()

    id_token = auth_header.split("Bearer ")[1]

    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
    except Exception as e:
        print("DEBUG: token verification failed:", repr(e)) 
        return AuthResult()

    email = decoded_token.get("email")
    if not email:
        return AuthResult()

    django_user = User.objects.filter(email=email, is_staff=True).first()
    observer = Observer.objects.filter(email=email).first()
    

    return (
        AuthResult(django_user=django_user,observer=observer)
    )  


def require_roles(*roles):
    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            identity = resolve_request_identity(request)
            request.identity = identity
            

            if (
                ("admin" in roles and identity.is_admin)
                or ("staff" in roles and identity.is_staff)
                or ("observer" in roles and identity.is_observer)
            ):
                return view_func(request, *args, **kwargs)

            return response.Response(
                {"message": "Not authorized"},
                status=403,
            )

        return wrapper

    return decorator


def filter_by_identity(queryset, request, owner_field="observer"):
    identity=resolve_request_identity(request)
    if identity.is_admin or identity.is_staff:
        return queryset

    return queryset.filter(**{owner_field: identity.observer})
