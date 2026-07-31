from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from category.models import Category
from question.models import Question
from subcategory.models import Subcategory
from survey.models import Survey
from zone.models import Zone


class QuestionViewSetTests(APITestCase):

    def setUp(self):

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

        self.question = Question.objects.create(
            subcategory=self.subcategory,
            code="Q1",
            question_type="single",
            description="Question 1",
            position=1,
        )
        self.question.survey.add(self.survey)

        self.list_url = reverse("question-list")

    @patch("users.permissions.QuestionPermission.has_permission", return_value=True)
    def test_list_questions(self, mock_permission):

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["code"], "Q1")

    @patch("users.permissions.QuestionPermission.has_permission", return_value=True)
    def test_retrieve_question(self, mock_permission):

        url = reverse("question-detail", args=[self.question.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], "Q1")

    @patch("users.permissions.QuestionPermission.has_permission", return_value=True)
    def test_create_question(self, mock_permission):

        response = self.client.post(
            self.list_url,
            {
                "subcategory": self.subcategory.id,
                "code": "Q2",
                "question_type": "single",
                "description": "Question 2",
                "survey": [self.survey.id],
                "position": 2,
                "is_required": True,
                "input_type": Question.InputType.NUMERIC,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), 2)

    @patch("users.permissions.QuestionPermission.has_permission", return_value=True)
    def test_update_question(self, mock_permission):

        url = reverse("question-detail", args=[self.question.id])

        response = self.client.put(
            url,
            {
                "subcategory": self.subcategory.id,
                "code": "Q1",
                "question_type": "text",
                "description": "Updated question",
                "survey": [self.survey.id],
                "position": 5,
                "is_required": False,
                "input_type": Question.InputType.TEXT,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.question.refresh_from_db()

        self.assertEqual(self.question.description, "Updated question")
        self.assertEqual(self.question.position, 5)
        self.assertEqual(self.question.input_type, Question.InputType.TEXT)
        self.assertFalse(self.question.is_required)

    @patch("users.permissions.QuestionPermission.has_permission", return_value=True)
    def test_partial_update_question(self, mock_permission):

        url = reverse("question-detail", args=[self.question.id])

        response = self.client.patch(
            url,
            {
                "description": "Patched description",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.question.refresh_from_db()

        self.assertEqual(
            self.question.description,
            "Patched description",
        )

    @patch("users.permissions.QuestionPermission.has_permission", return_value=True)
    def test_delete_question(self, mock_permission):

        url = reverse("question-detail", args=[self.question.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Question.objects.count(), 0)
