from django.db import IntegrityError
from django.test import TestCase

from category.models import Category
from observer.models import Observer
from option.models import Option
from question.models import Question
from response.models import Response, QuestionCommentAnswer
from subcategory.models import Subcategory
from survey.models import Survey
from surveysession.models import Surveysession
from visit.models import Visit
from zone.models import Zone


class ResponseModelTests(TestCase):

    def setUp(self):

        self.zone = Zone.objects.create(name="Zone A")

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

    def test_create_response(self):
        self.assertEqual(Response.objects.count(), 1)

    def test_default_values(self):
        self.assertEqual(self.response.numeric_value, 5)
        self.assertIsNone(self.response.text_value)

    def test_string_representation(self):
        expected = (
            f"survey:{self.survey.name}"
            f"-session:{self.session.number_session}"
            f"-visita:{self.visit.visit_number}"
            f"-question:{self.question}"
        )

        self.assertEqual(str(self.response), expected)

    def test_update_response(self):
        self.response.numeric_value = 10
        self.response.save()

        self.response.refresh_from_db()

        self.assertEqual(self.response.numeric_value, 10)

    def test_delete_response(self):
        self.response.delete()

        self.assertEqual(Response.objects.count(), 0)

    def test_unique_visit_question_constraint(self):
        with self.assertRaises(IntegrityError):
            Response.objects.create(
                visita=self.visit,
                question=self.question,
                option=self.option,
            )


class QuestionCommentAnswerModelTests(TestCase):

    def setUp(self):

        self.zone = Zone.objects.create(name="Zone A")

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
            comment="Everything looks good.",
        )

    def test_create_comment(self):
        self.assertEqual(QuestionCommentAnswer.objects.count(), 1)

    def test_string_representation(self):
        expected = f"Comment by {self.visit} on {self.question}"
        self.assertEqual(str(self.comment), expected)

    def test_update_comment(self):
        self.comment.comment = "Updated comment"
        self.comment.save()

        self.comment.refresh_from_db()

        self.assertEqual(self.comment.comment, "Updated comment")

    def test_delete_comment(self):
        self.comment.delete()

        self.assertEqual(QuestionCommentAnswer.objects.count(), 0)

    def test_unique_comment_constraint(self):
        with self.assertRaises(IntegrityError):
            QuestionCommentAnswer.objects.create(
                visita=self.visit,
                question=self.question,
                comment="Duplicate",
            )
