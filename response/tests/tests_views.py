from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from campus.models import Campus
from category.models import Category
from observer.models import Observer
from option.models import Option
from question.models import Question
from response.models import Response
from subcategory.models import Subcategory
from survey.models import Survey
from surveysession.models import Surveysession
from visit.models import Visit
from zone.models import Zone


class ResponseViewSetTests(APITestCase):

    def setUp(self):

        self.campus = Campus.objects.create(name="Main Campus")

        self.zone = Zone.objects.create(
            name="Zone A",
            campus=self.campus,
        )

        self.category = Category.objects.create(
            name="Infrastructure",
            target_zone_type=Zone.ZoneType.OPEN,
        )

        self.subcategory = Subcategory.objects.create(
            name="Doors",
            category=self.category,
        )

        self.survey = Survey.objects.create(
            name="Survey",
            topic="Campus",
            version="1.0",
            description="Test survey",
        )

        self.observer = Observer.objects.create(
            name="Observer",
            email="observer@test.com",
        )

        self.session = Surveysession.objects.create(
            survey=self.survey,
            observer=self.observer,
            zone=self.zone,
            number_session=1,
        )

        self.visit = Visit.objects.create(
            surveysession=self.session,
            visit_number=1,
        )

        self.option = Option.objects.create(
            description="Yes",
            type=Option.InputType.NUMERIC,
        )

        self.question = Question.objects.create(
            subcategory=self.subcategory,
            code="Q1",
            question_type="single",
            description="Question",
        )
        self.question.survey.add(self.survey)

        self.response = Response.objects.create(
            visita=self.visit,
            question=self.question,
            option=self.option,
            numeric_value=5,
        )

        self.list_url = reverse("response-list")

    @patch(
        "users.permissions.ResponsePermissions.has_permission",
        return_value=True,
    )
    def test_list_responses(self, mock_permission):

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    @patch(
        "users.permissions.ResponsePermissions.has_permission",
        return_value=True,
    )
    def test_create_response(self, mock_permission):

        question2 = Question.objects.create(
            subcategory=self.subcategory,
            code="Q2",
            question_type="single",
            description="Question 2",
        )
        question2.survey.add(self.survey)

        response = self.client.post(
            self.list_url,
            {
                "visita": self.visit.id,
                "question": question2.id,
                "option": self.option.id,
                "numeric_value": 10,
                "text_value": None,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Response.objects.count(), 2)

    @patch(
        "users.permissions.ResponsePermissions.has_permission",
        return_value=True,
    )
    @patch(
        "users.permissions.ResponsePermissions.has_object_permission",
        return_value=True,
    )
    def test_retrieve_response(
        self,
        mock_object_permission,
        mock_permission,
    ):

        url = reverse("response-detail", args=[self.response.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["numeric_value"], 5)

    @patch(
        "users.permissions.ResponsePermissions.has_permission",
        return_value=True,
    )
    @patch(
        "users.permissions.ResponsePermissions.has_object_permission",
        return_value=True,
    )
    def test_update_response(
        self,
        mock_object_permission,
        mock_permission,
    ):

        url = reverse("response-detail", args=[self.response.id])

        response = self.client.put(
            url,
            {
                "visita": self.visit.id,
                "question": self.question.id,
                "option": self.option.id,
                "numeric_value": 20,
                "text_value": "Updated",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.response.refresh_from_db()

        self.assertEqual(self.response.numeric_value, 20)
        self.assertEqual(self.response.text_value, "Updated")

    @patch(
        "users.permissions.ResponsePermissions.has_permission",
        return_value=True,
    )
    @patch(
        "users.permissions.ResponsePermissions.has_object_permission",
        return_value=True,
    )
    def test_partial_update_response(
        self,
        mock_object_permission,
        mock_permission,
    ):

        url = reverse("response-detail", args=[self.response.id])

        response = self.client.patch(
            url,
            {
                "numeric_value": 99,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.response.refresh_from_db()

        self.assertEqual(self.response.numeric_value, 99)

    @patch(
        "users.permissions.ResponsePermissions.has_permission",
        return_value=True,
    )
    @patch(
        "users.permissions.ResponsePermissions.has_object_permission",
        return_value=True,
    )
    def test_delete_response(
        self,
        mock_object_permission,
        mock_permission,
    ):

        url = reverse("response-detail", args=[self.response.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Response.objects.count(), 0)
