from firebase_admin import auth as firebase_auth
from django.contrib.auth import get_user_model
from observer.models import Observer

User = get_user_model()


class AuthResult:
    def __init__(self, django_user=None, observer=None):
        self.django_user = django_user
        self.observer = observer

    @property
    def is_admin(self):
        return self.django_user is not None and self.django_user.is_staff

    @property
    def is_observer(self):
        return self.observer is not None

    @property
    def is_authenticated(self):
        return self.django_user is not None or self.observer is not None


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
    if django_user:
        return AuthResult(django_user=django_user)

    observer = Observer.objects.filter(email=email).first()
    if observer:
        return AuthResult(observer=observer)

    return (
        AuthResult()
    )  
