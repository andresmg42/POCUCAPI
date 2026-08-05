from types import SimpleNamespace
from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from campus.models import Campus
from observer.models import Observer
from survey.models import Survey
from surveysession.models import Surveysession
from visit.models import Visit
from visit.views import VisitViewSet, get_visits_by_id_session, update_start_date
from zone.models import Zone


class VisitViewSetTests(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.list_view = VisitViewSet.as_view({"get": "list", "post": "create"})
        self.detail_view = VisitViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        )

        self.campus = Campus.objects.create(name="Main Campus")
        self.zone = Zone.objects.create(name="Zone 1", campus=self.campus)
        self.observer = Observer.objects.create(
            name="Observer",
            email="observer@example.com",
        )
        self.other_observer = Observer.objects.create(
            name="Other Observer",
            email="other@example.com",
        )
        self.survey = Survey.objects.create(
            name="Survey",
            topic="General",
            version="1.0",
            description="Survey description",
        )
        self.session = Surveysession.objects.create(
            zone=self.zone,
            observer=self.observer,
            survey=self.survey,
            url="https://example.com/session",
            number_session=1,
            observational_distance="10m",
        )
        self.other_session = Surveysession.objects.create(
            zone=self.zone,
            observer=self.other_observer,
            survey=self.survey,
            url="https://example.com/session-2",
            number_session=1,
            observational_distance="10m",
        )
        self.visit = Visit.objects.create(
            surveysession=self.session,
            visit_number=1,
        )
        self.other_visit = Visit.objects.create(
            surveysession=self.other_session,
            visit_number=1,
        )

    def _identity(self, role, observer=None):
        return SimpleNamespace(
            is_authenticated=True,
            is_admin=role == "admin",
            is_staff=role == "staff",
            is_observer=role == "observer",
            role=role,
            observer=observer,
        )

    def test_list_visits_as_admin(self):
        request = self.factory.get("/visit/")

        with patch("users.permissions.resolve_request_identity", return_value=self._identity("admin")):
            response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_visit(self):
        request = self.factory.get("/visit/1/")

        with patch("users.permissions.resolve_request_identity", return_value=self._identity("admin")):
            response = self.detail_view(request, pk=self.visit.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["visit_number"], 1)

    def test_create_visit_as_observer_for_own_session(self):
        request = self.factory.post(
            "/visit/",
            {
                "surveysession": self.session.id,
            },
        )

        with patch("users.permissions.resolve_request_identity", return_value=self._identity("observer", self.observer)):
            response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Visit.objects.count(), 3)

    def test_update_visit(self):
        request = self.factory.put(
            "/visit/1/",
            {
                "surveysession": self.session.id,
                "visit_number": 1,
                "state": 1,
            },
        )

        with patch("users.permissions.resolve_request_identity", return_value=self._identity("admin")):
            response = self.detail_view(request, pk=self.visit.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.visit.refresh_from_db()

        self.assertEqual(self.visit.state, 1)

    def test_delete_visit(self):
        request = self.factory.delete("/visit/1/")

        with patch("users.permissions.resolve_request_identity", return_value=self._identity("admin")):
            response = self.detail_view(request, pk=self.visit.id)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Visit.objects.count(), 1)


class VisitFunctionViewTests(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

        self.campus = Campus.objects.create(name="Main Campus")
        self.zone = Zone.objects.create(name="Zone 1", campus=self.campus)
        self.observer = Observer.objects.create(
            name="Observer",
            email="observer@example.com",
        )
        self.survey = Survey.objects.create(
            name="Survey",
            topic="General",
            version="1.0",
            description="Survey description",
        )
        self.session = Surveysession.objects.create(
            zone=self.zone,
            observer=self.observer,
            survey=self.survey,
            url="https://example.com/session",
            number_session=1,
            observational_distance="10m",
        )
        self.visit = Visit.objects.create(
            surveysession=self.session,
            visit_number=1,
        )

    def _identity(self, role, observer=None):
        return SimpleNamespace(
            is_authenticated=True,
            is_admin=role == "admin",
            is_staff=role == "staff",
            is_observer=role == "observer",
            role=role,
            observer=observer,
        )

    def test_get_visits_by_id_session(self):
        request = self.factory.get(
            "/visit/sessionvisits/",
            {"surveysession_id": self.session.id},
        )

        with patch("users.user_utils.resolve_request_identity", return_value=self._identity("observer", self.observer)):
            response = get_visits_by_id_session(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["visit_number"], 1)

    def test_get_visits_by_id_session_invalid_param(self):
        request = self.factory.get(
            "/visit/sessionvisits/",
            {"surveysession_id": "undefined"},
        )

        with patch("users.user_utils.resolve_request_identity", return_value=self._identity("observer", self.observer)):
            response = get_visits_by_id_session(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {"message": "id invalid in get_visits_by_id_session"},
        )

    def test_update_start_date(self):
        request = self.factory.post(
            "/visit/update_start_date/",
            {"visit_id": self.visit.id},
        )

        with patch("users.user_utils.resolve_request_identity", return_value=self._identity("observer", self.observer)):
            response = update_start_date(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.visit.refresh_from_db()

        self.assertEqual(self.visit.state, 1)
        self.assertIsNotNone(self.visit.visit_start_date_time)

    def test_update_start_date_missing_visit_id(self):
        request = self.factory.post(
            "/visit/update_start_date/",
            {"visit_id": ""},
        )

        with patch("users.user_utils.resolve_request_identity", return_value=self._identity("observer", self.observer)):
            response = update_start_date(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"message": "visit_id is required"})