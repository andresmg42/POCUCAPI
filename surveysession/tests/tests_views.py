from types import SimpleNamespace
from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from campus.models import Campus
from category.models import Category
from observer.models import Observer
from option.models import Option
from question.models import Question
from subcategory.models import Subcategory
from survey.models import Survey
from surveysession.models import Surveysession
from surveysession.views import (
    SurveysessionViewSet,
    get_surveysession_by_survey_id,
    update_start_session,
)
from zone.models import Zone


class SurveysessionViewSetTests(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.list_view = SurveysessionViewSet.as_view({"get": "list", "post": "create"})
        self.detail_view = SurveysessionViewSet.as_view(
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
        self.category = Category.objects.create(name="Infrastructure")
        self.subcategory = Subcategory.objects.create(
            category=self.category,
            name="Doors",
        )
        self.option = Option.objects.create(
            description="Yes",
            type=Option.InputType.NUMERIC,
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

    def _identity(self, role, observer=None):
        return SimpleNamespace(
            is_authenticated=True,
            is_admin=role == "admin",
            is_staff=role == "staff",
            is_observer=role == "observer",
            role=role,
            observer=observer,
        )

    def test_list_sessions_as_admin(self):
        request = self.factory.get("/surveysession/")

        with patch("users.permissions.resolve_request_identity", return_value=self._identity("admin")):
            response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_session(self):
        request = self.factory.get("/surveysession/1/")

        with patch("users.permissions.resolve_request_identity", return_value=self._identity("admin")):
            response = self.detail_view(request, pk=self.session.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["url"], "https://example.com/session")

    def test_create_session_as_observer_without_observer_field(self):
        request = self.factory.post(
            "/surveysession/",
            {
                "zone": self.zone.id,
                "survey": self.survey.id,
                "observational_distance": "15m",
                "url": "https://example.com/new-session",
            },
        )

        with patch("users.permissions.resolve_request_identity", return_value=self._identity("observer", self.observer)):
            response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Surveysession.objects.count(), 3)

    def test_update_session(self):
        request = self.factory.put(
            "/surveysession/1/",
            {
                "zone": self.zone.id,
                "observer": self.observer.email,
                "survey": self.survey.id,
                "observational_distance": "20m",
                "url": "https://example.com/updated",
                "visit_number": 6,
                "state": 1,
            },
        )

        with patch("users.permissions.resolve_request_identity", return_value=self._identity("admin")):
            response = self.detail_view(request, pk=self.session.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.session.refresh_from_db()

        self.assertEqual(self.session.url, "https://example.com/updated")
        self.assertEqual(self.session.observational_distance, "20m")

    def test_delete_session(self):
        request = self.factory.delete("/surveysession/1/")

        with patch("users.permissions.resolve_request_identity", return_value=self._identity("admin")):
            response = self.detail_view(request, pk=self.session.id)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Surveysession.objects.count(), 1)


class SurveysessionFunctionViewTests(APITestCase):

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
        self.category = Category.objects.create(name="Infrastructure")
        self.subcategory = Subcategory.objects.create(
            category=self.category,
            name="Doors",
        )
        self.option = Option.objects.create(
            description="Yes",
            type=Option.InputType.NUMERIC,
        )
        self.session = Surveysession.objects.create(
            zone=self.zone,
            observer=self.observer,
            survey=self.survey,
            url="https://example.com/session",
            number_session=1,
            observational_distance="10m",
        )

        self.parent_question = Question.objects.create(
            subcategory=self.subcategory,
            code="Q1",
            question_type="single",
            description="Parent question",
            position=1,
        )
        self.parent_question.survey.add(self.survey)
        self.parent_question.options.add(self.option)

    def _identity(self, role, observer=None):
        return SimpleNamespace(
            is_authenticated=True,
            is_admin=role == "admin",
            is_staff=role == "staff",
            is_observer=role == "observer",
            role=role,
            observer=observer,
        )

    def test_get_surveysession_by_survey_id(self):
        request = self.factory.get(
            "/surveysession/get_survey_session_by_survey_id",
            {"survey_id": self.survey.id},
        )

        with patch("users.user_utils.resolve_request_identity", return_value=self._identity("observer", self.observer)):
            response = get_surveysession_by_survey_id(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["url"], "https://example.com/session")

    def test_get_surveysession_by_survey_id_invalid_param(self):
        request = self.factory.get(
            "/surveysession/get_survey_session_by_survey_id",
            {"survey_id": "undefined"},
        )

        with patch("users.user_utils.resolve_request_identity", return_value=self._identity("observer", self.observer)):
            response = get_surveysession_by_survey_id(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {"message": "survey_id invalid in get_surveysession_by_id"},
        )

    def test_update_start_session(self):
        request = self.factory.post(
            "/surveysession/update_start_session/",
            {"surveysession_id": self.session.id},
        )

        with patch("users.user_utils.resolve_request_identity", return_value=self._identity("observer", self.observer)):
            response = update_start_session(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.session.refresh_from_db()

        self.assertEqual(self.session.state, 1)
        self.assertIsNotNone(self.session.start_date)

    def test_update_start_session_missing_session_id(self):
        request = self.factory.post("/surveysession/update_start_session/", {})

        with patch("users.user_utils.resolve_request_identity", return_value=self._identity("observer", self.observer)):
            response = update_start_session(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"message": "session_id is required"})