from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from category.models import Category
from subcategory.models import Subcategory
from question.models import Question
from survey.models import Survey
from surveysession.models import Surveysession
from visit.models import Visit
from response.models import Response
from zone.models import Zone
from observer.models import Observer

User = get_user_model()


def make_identity(role="admin"):
    identity = MagicMock()
    identity.is_authenticated = True
    identity.role = role
    identity.is_admin = role == "admin"
    identity.is_staff = role == "staff"
    identity.is_observer = role == "observer"
    identity.observer = None
    return identity


class GetCategoriesTests(APITestCase):

    def setUp(self):

        self.url = reverse("get_categories")

        self.zone = Zone.objects.create(
            name="Open",
            zone_type=Zone.ZoneType.OPEN,
            number=1,
        )

        self.category = Category.objects.create(
            name="Category", target_zone_type=Zone.ZoneType.OPEN
        )

        self.subcategory = Subcategory.objects.create(
            name="Subcategory", category=self.category
        )

        self.survey = Survey.objects.create(
            name="Survey", topic="Topic", version="1", description="desc"
        )

        self.question = Question.objects.create(
            subcategory=self.subcategory,
            code="Q1",
            description="Question",
            question_type="text",
            input_type=Question.InputType.TEXT,
        )

        self.question.survey.add(self.survey)

        self.observer = Observer.objects.create(
            name="Observer", email="observer@test.com"
        )

        self.session = Surveysession.objects.create(
            observer=self.observer,
            survey=self.survey,
            zone=self.zone,
            url="url",
            number_session=1,
            observational_distance="5",
        )

    def test_missing_param(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_session(self):

        response = self.client.get(self.url, {"surveysession_id": 999})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_returns_categories(self):

        response = self.client.get(self.url, {"surveysession_id": self.session.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Category")


class QuestionCompletedTests(APITestCase):

    def setUp(self):

        self.url = reverse("questions_of_category_completed")

        self.zone = Zone.objects.create(
            name="Zone",
            zone_type=Zone.ZoneType.OPEN,
            number=1,
        )

        self.category = Category.objects.create(
            name="Category", target_zone_type=Zone.ZoneType.OPEN
        )

        self.subcategory = Subcategory.objects.create(
            name="Sub", category=self.category
        )

        self.survey = Survey.objects.create(
            name="Survey", topic="Topic", version="1", description="desc"
        )

        self.question = Question.objects.create(
            subcategory=self.subcategory,
            code="Q1",
            description="Question",
            question_type="text",
            is_required=True,
            input_type=Question.InputType.TEXT,
        )

        self.question.survey.add(self.survey)

        self.observer = Observer.objects.create(
            name="Observer", email="observer@test.com"
        )

        self.session = Surveysession.objects.create(
            observer=self.observer,
            survey=self.survey,
            zone=self.zone,
            url="url",
            number_session=1,
            observational_distance="5",
        )

        self.visit = Visit.objects.create(surveysession=self.session, visit_number=1)

    def test_missing_parameters(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_completed(self):

        response = self.client.get(
            self.url, {"visit_id": self.visit.id, "category_id": self.category.id}
        )

        self.assertFalse(response.data["is_completed"])

    def test_completed(self):

        Response.objects.create(
            visita=self.visit, question=self.question, text_value="answer"
        )

        response = self.client.get(
            self.url, {"visit_id": self.visit.id, "category_id": self.category.id}
        )

        self.assertTrue(response.data["is_completed"])


class CategoryViewSetTests(APITestCase):

    def setUp(self):

        self.url = reverse("category-list")

        self.category = Category.objects.create(name="Category")

    def admin(self):
        return patch(
            "users.permissions.resolve_request_identity",
            return_value=make_identity("admin"),
        )

    def test_list(self):

        with self.admin():
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):

        with self.admin():
            response = self.client.post(self.url, {"name": "New"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update(self):

        with self.admin():
            response = self.client.patch(
                reverse("category-detail", args=[self.category.id]), {"name": "Updated"}
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete(self):

        with self.admin():
            response = self.client.delete(
                reverse("category-detail", args=[self.category.id])
            )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
