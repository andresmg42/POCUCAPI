from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import TestCase

from users.user_utils import require_roles


class RequireRolesTests(TestCase):

    def setUp(self):
        self.request = SimpleNamespace(headers={})

    def make_identity(self, role):
        observer = object() if role == "observer" else None

        return SimpleNamespace(
            is_authenticated=True,
            is_admin=role == "admin",
            is_staff=role == "staff",
            is_observer=role == "observer",
            role=role,
            observer=observer,
        )

    def test_require_roles_allows_authorized_role(self):
        identity = self.make_identity("staff")
        view_func = Mock(return_value="allowed")

        decorated = require_roles("admin", "staff")(view_func)

        with patch("users.user_utils.resolve_request_identity", return_value=identity):
            response = decorated(self.request)

        self.assertEqual(response, "allowed")
        self.assertIs(self.request.identity, identity)
        view_func.assert_called_once_with(self.request)

    def test_require_roles_denies_unauthorized_role(self):
        identity = self.make_identity("observer")
        view_func = Mock(return_value="allowed")

        decorated = require_roles("admin", "staff")(view_func)

        with patch("users.user_utils.resolve_request_identity", return_value=identity):
            response = decorated(self.request)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {"message": "Not authorized"})
        self.assertIs(self.request.identity, identity)
        view_func.assert_not_called()

    def test_require_roles_denies_unauthenticated_request(self):
        identity = SimpleNamespace(
            is_authenticated=False,
            is_admin=False,
            is_staff=False,
            is_observer=False,
            role=None,
            observer=None,
        )
        view_func = Mock(return_value="allowed")

        decorated = require_roles("admin")(view_func)

        with patch("users.user_utils.resolve_request_identity", return_value=identity):
            response = decorated(self.request)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {"message": "Not authorized"})
        self.assertIs(self.request.identity, identity)
        view_func.assert_not_called()