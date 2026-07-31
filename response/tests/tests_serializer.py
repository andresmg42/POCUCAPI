from django.test import TestCase

from category.models import Category
from campus.models import Campus
from observer.models import Observer
from option.models import Option
from question.models import Question
from response.models import Response, QuestionCommentAnswer
from response.serializer import (
    ResponseSerializer,
    QuestionCommentAnswerSerializer,
)
from subcategory.models import Subcategory
from survey.models import Survey
from surveysession.models import Surveysession
from visit.models import Visit
from zone.models import Zone


class ResponseSerializerTests(TestCase):

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
            description="Test",
        )

        self.observer = Observer.objects.create(
            name="John",
            email="john@test.com",
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

        self.parent = Question.objects.create(
            subcategory=self.subcategory,
            code="P1",
            question_type="single",
            description="Parent Question",
        )
        self.parent.survey.add(self.survey)

        self.question = Question.objects.create(
            subcategory=self.subcategory,
            code="Q1",
            question_type="single",
            description="Child Question",
            parent_question=self.parent,
        )
        self.question.survey.add(self.survey)

        self.response = Response.objects.create(
            visita=self.visit,
            question=self.question,
            option=self.option,
            numeric_value=5,
            text_value="Good",
        )

    def test_serializer_contains_expected_fields(self):

        serializer = ResponseSerializer(self.response)

        expected = {
            "id",
            "option",
            "visita",
            "question",
            "numeric_value",
            "text_value",
            "surveysession_id",
            "survey",
            "zone",
            "campus",
            "question_description",
            "category",
            "subcategory",
            "observer",
            "observer_email",
            "observer_id",
            "survey_id",
            "zone_id",
            "campus_id",
            "subcategory_id",
            "category_id",
            "parent_question",
            "parent_question_id",
            "question_code",
        }

        self.assertEqual(set(serializer.data.keys()), expected)

    def test_read_only_fields(self):

        serializer = ResponseSerializer(self.response)

        self.assertEqual(serializer.data["observer"], "John")
        self.assertEqual(serializer.data["observer_email"], "john@test.com")
        self.assertEqual(serializer.data["survey"], "Survey")
        self.assertEqual(serializer.data["zone"], "Zone A")
        self.assertEqual(serializer.data["campus"], "Main Campus")
        self.assertEqual(serializer.data["category"], "Infrastructure")
        self.assertEqual(serializer.data["subcategory"], "Doors")
        self.assertEqual(serializer.data["question_description"], "Child Question")
        self.assertEqual(serializer.data["question_code"], "Q1")
        self.assertEqual(serializer.data["parent_question"], "Parent Question")

    def test_numeric_and_text_values(self):

        serializer = ResponseSerializer(self.response)

        self.assertEqual(serializer.data["numeric_value"], 5)
        self.assertEqual(serializer.data["text_value"], "Good")

    def test_serializer_valid_data(self):

        serializer = ResponseSerializer(
            data={
                "option": self.option.id,
                "visita": self.visit.id,
                "question": self.parent.id,
                "numeric_value": 10,
            }
        )

        self.assertTrue(serializer.is_valid())

    def test_serializer_invalid_without_visit(self):

        serializer = ResponseSerializer(
            data={
                "question": self.parent.id,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("visita", serializer.errors)


class QuestionCommentAnswerSerializerTests(TestCase):

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
            description="Test",
        )

        self.observer = Observer.objects.create(
            name="John",
            email="john@test.com",
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

        self.question = Question.objects.create(
            subcategory=self.subcategory,
            code="Q1",
            question_type="single",
            description="Question",
        )
        self.question.survey.add(self.survey)

        self.comment = QuestionCommentAnswer.objects.create(
            visita=self.visit,
            question=self.question,
            comment="Everything OK",
        )

    def test_comment_serializer_fields(self):

        serializer = QuestionCommentAnswerSerializer(self.comment)

        self.assertEqual(
            set(serializer.data.keys()),
            {"id", "visita", "question", "comment"},
        )

    def test_comment_serializer_data(self):

        serializer = QuestionCommentAnswerSerializer(self.comment)

        self.assertEqual(serializer.data["comment"], "Everything OK")


    def test_comment_serializer_valid_data(self):

        other_question = Question.objects.create(
            subcategory=self.subcategory,
            code="Q2",
            question_type="single",
            description="Another question",
        )
        other_question.survey.add(self.survey)

        serializer = QuestionCommentAnswerSerializer(
            data={
                "visita": self.visit.id,
                "question": other_question.id,
                "comment": "New comment",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
