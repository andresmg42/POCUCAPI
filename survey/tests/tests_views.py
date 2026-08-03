from unittest.mock import patch
from types import SimpleNamespace

from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from category.models import Category
from observer.models import Observer
from option.models import Option
from question.models import Question
from subcategory.models import Subcategory
from survey.models import Survey
from survey.views import SurveyViewSet, get_questions_and_options
from surveysession.models import Surveysession
from zone.models import Zone


class SurveyViewSetTests(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.list_view = SurveyViewSet.as_view({"get": "list", "post": "create"})
        self.detail_view = SurveyViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        )

        self.first = Survey.objects.create(
            name="First",
            topic="General",
            version="1.0",
            description="First survey",
            image_url="https://example.com/first.png",
        )

        self.second = Survey.objects.create(
            name="Second",
            topic="General",
            version="1.1",
            description="Second survey",
            image_url="https://example.com/second.png",
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
        self.zone = Zone.objects.create(name="Zone 1")
        self.observer = Observer.objects.create(
            name="Observer",
            email="observer@example.com",
        )
        self.session = Surveysession.objects.create(
            zone=self.zone,
            observer=self.observer,
            survey=self.first,
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
        self.parent_question.survey.add(self.first)
        self.parent_question.options.add(self.option)

        self.child_question = Question.objects.create(
            subcategory=self.subcategory,
            code="Q2",
            question_type="single",
            description="Child question",
            parent_question=self.parent_question,
            position=2,
        )
        self.child_question.survey.add(self.first)

    def test_list_surveys(self):
        request = self.factory.get("/survey/surveys/")

        with patch("users.permissions.SurveyPermissions.has_permission", return_value=True):
            response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_survey(self):
        request = self.factory.get("/survey/surveys/1/")

        with patch("users.permissions.SurveyPermissions.has_permission", return_value=True):
            response = self.detail_view(request, pk=self.first.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "First")

    def test_create_survey(self):
        request = self.factory.post(
            "/survey/surveys/",
            {
                "name": "New Survey",
                "topic": "General",
                "version": "2.0",
                "description": "Created survey",
                "image_url": "https://example.com/new.png",
            },
        )

        with patch("users.permissions.SurveyPermissions.has_permission", return_value=True):
            response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Survey.objects.count(), 3)

    def test_update_survey(self):
        request = self.factory.put(
            "/survey/surveys/1/",
            {
                "name": "Updated Survey",
                "topic": "Updated Topic",
                "version": "2.0",
                "description": "Updated description",
                "image_url": "https://example.com/updated.png",
            },
        )

        with patch("users.permissions.SurveyPermissions.has_permission", return_value=True):
            response = self.detail_view(request, pk=self.first.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.first.refresh_from_db()

        self.assertEqual(self.first.name, "Updated Survey")
        self.assertEqual(self.first.topic, "Updated Topic")
        self.assertEqual(self.first.version, "2.0")
        self.assertEqual(self.first.description, "Updated description")
        self.assertEqual(self.first.image_url, "https://example.com/updated.png")

    def test_delete_survey(self):
        request = self.factory.delete("/survey/surveys/1/")

        with patch("users.permissions.SurveyPermissions.has_permission", return_value=True):
            response = self.detail_view(request, pk=self.first.id)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Survey.objects.count(), 1)

    def test_get_questions_and_options(self):
        request = self.factory.get(
            "/survey/get_survey/",
            {
                "surveysession_id": self.session.id,
                "category_id": self.category.id,
            },
        )

        identity = SimpleNamespace(
            is_authenticated=True,
            is_admin=False,
            is_staff=True,
            is_observer=False,
            role="staff",
            observer=None,
        )

        with patch("users.user_utils.resolve_request_identity", return_value=identity):
            response = get_questions_and_options(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["code"], "Q1")
        self.assertEqual(response.data[0]["options"][0]["description"], "Yes")
        self.assertEqual(response.data[0]["sub_questions"][0]["code"], "Q2")

    def test_get_questions_and_options_invalid_params(self):
        request = self.factory.get(
            "/survey/get_survey/",
            {
                "surveysession_id": "undefined",
                "category_id": "undefined",
            },
        )

        identity = SimpleNamespace(
            is_authenticated=True,
            is_admin=False,
            is_staff=True,
            is_observer=False,
            role="staff",
            observer=None,
        )

        with patch("users.user_utils.resolve_request_identity", return_value=identity):
            response = get_questions_and_options(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {"message": "id invalid in get_questions_and_options"},
        )