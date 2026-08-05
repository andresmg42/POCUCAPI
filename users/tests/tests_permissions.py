from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase

from users.permissions import (
	OptionPermissions,
	ResponsePermissions,
	RoleBasedPermission,
	SurveySessionPermissions,
	VisitPermissions,
)


class RoleBasedPermissionTests(TestCase):

	def setUp(self):
		self.permission = RoleBasedPermission()
		self.request = SimpleNamespace(headers={})
		self.view = SimpleNamespace(action="list")

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

	def test_has_permission_rejects_unauthenticated_requests(self):
		identity = SimpleNamespace(is_authenticated=False)

		with patch("users.permissions.resolve_request_identity", return_value=identity):
			result = self.permission.has_permission(self.request, self.view)

		self.assertFalse(result)
		self.assertIs(self.request.identity, identity)

	def test_has_permission_allows_allowed_role_for_action(self):
		identity = self.make_identity("observer")

		with patch("users.permissions.resolve_request_identity", return_value=identity):
			result = self.permission.has_permission(self.request, self.view)

		self.assertTrue(result)
		self.assertIs(self.request.identity, identity)

	def test_has_permission_rejects_disallowed_role_for_action(self):
		identity = self.make_identity("observer")
		self.view.action = "create"

		with patch("users.permissions.resolve_request_identity", return_value=identity):
			result = self.permission.has_permission(self.request, self.view)

		self.assertFalse(result)


class ResponsePermissionTests(TestCase):

	def setUp(self):
		self.permission = ResponsePermissions()
		self.request = SimpleNamespace(headers={})
		self.view = SimpleNamespace(action="update")

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

	def test_has_permission_allows_observer_on_create(self):
		self.view.action = "create"
		identity = self.make_identity("observer")

		with patch("users.permissions.resolve_request_identity", return_value=identity):
			result = self.permission.has_permission(self.request, self.view)

		self.assertTrue(result)

	def test_has_object_permission_allows_admin(self):
		identity = self.make_identity("admin")
		obj = SimpleNamespace(observer=object())

		with patch("users.permissions.resolve_request_identity", return_value=identity):
			result = self.permission.has_object_permission(self.request, self.view, obj)

		self.assertTrue(result)

	def test_has_object_permission_allows_matching_observer(self):
		identity = self.make_identity("observer")
		obj = SimpleNamespace(observer=identity.observer)

		with patch("users.permissions.resolve_request_identity", return_value=identity):
			result = self.permission.has_object_permission(self.request, self.view, obj)

		self.assertTrue(result)

	def test_has_object_permission_denies_staff_destroy(self):
		self.view.action = "destroy"
		identity = self.make_identity("staff")
		obj = SimpleNamespace(observer=object())

		with patch("users.permissions.resolve_request_identity", return_value=identity):
			result = self.permission.has_object_permission(self.request, self.view, obj)

		self.assertFalse(result)


class SurveySessionPermissionTests(TestCase):

	def setUp(self):
		self.permission = SurveySessionPermissions()
		self.request = SimpleNamespace(headers={})
		self.view = SimpleNamespace(action="update")

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

	def test_has_object_permission_allows_matching_observer(self):
		identity = self.make_identity("observer")
		obj = SimpleNamespace(observer=identity.observer)

		with patch("users.permissions.resolve_request_identity", return_value=identity):
			result = self.permission.has_object_permission(self.request, self.view, obj)

		self.assertTrue(result)

	def test_has_object_permission_allows_staff_except_destroy(self):
		identity = self.make_identity("staff")
		obj = SimpleNamespace(observer=object())

		with patch("users.permissions.resolve_request_identity", return_value=identity):
			allowed = self.permission.has_object_permission(self.request, self.view, obj)

		self.assertTrue(allowed)

		self.view.action = "destroy"

		with patch("users.permissions.resolve_request_identity", return_value=identity):
			denied = self.permission.has_object_permission(self.request, self.view, obj)

		self.assertFalse(denied)


class VisitPermissionTests(TestCase):

	def setUp(self):
		self.permission = VisitPermissions()
		self.request = SimpleNamespace(headers={})
		self.view = SimpleNamespace(action="update")

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

	def test_has_object_permission_allows_observer_for_matching_session(self):
		identity = self.make_identity("observer")
		obj = SimpleNamespace(surveysession=SimpleNamespace(observer=identity.observer))

		with patch("users.permissions.resolve_request_identity", return_value=identity):
			result = self.permission.has_object_permission(self.request, self.view, obj)

		self.assertTrue(result)

	def test_has_object_permission_denies_staff_destroy(self):
		identity = self.make_identity("staff")
		obj = SimpleNamespace(surveysession=SimpleNamespace(observer=object()))
		self.view.action = "destroy"

		with patch("users.permissions.resolve_request_identity", return_value=identity):
			result = self.permission.has_object_permission(self.request, self.view, obj)

		self.assertFalse(result)
