from django.test import TestCase

from category.models import Category
from option.models import Option
from question.models import Question
from subcategory.models import Subcategory
from survey.models import Survey
from zone.models import Zone


class QuestionModelTests(TestCase):

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
            name="Survey 1",
            topic="Campus",
            version="1.0",
            description="Test survey",
        )

        self.option = Option.objects.create(
            description="Yes",
            type=Option.InputType.NUMERIC,
        )

        self.question = Question.objects.create(
            subcategory=self.subcategory,
            code="Q1",
            question_type="single",
            description="Is the door open?",
        )

        self.question.survey.add(self.survey)
        self.question.options.add(self.option)

    def test_create_question(self):
        self.assertEqual(Question.objects.count(), 1)

    def test_default_values(self):
        self.assertTrue(self.question.is_required)
        self.assertEqual(
            self.question.input_type,
            Question.InputType.NUMERIC,
        )
        self.assertEqual(self.question.position, 1.0)

    def test_string_representation(self):
        expected = (
            f"{self.survey.name}-"
            f"{self.category.name}-"
            f"{self.subcategory.name}-"
            f"{self.question.code}"
        )

        self.assertEqual(str(self.question), expected)

    def test_question_has_survey(self):
        self.assertEqual(
            self.question.survey.first(),
            self.survey,
        )

    def test_question_has_option(self):
        self.assertEqual(
            self.question.options.first(),
            self.option,
        )

    def test_parent_question_relationship(self):

        child = Question.objects.create(
            subcategory=self.subcategory,
            code="Q2",
            question_type="text",
            description="Child question",
            parent_question=self.question,
        )

        child.survey.add(self.survey)

        self.assertEqual(
            child.parent_question,
            self.question,
        )

        self.assertIn(
            child,
            self.question.child_questions.all(),
        )

    def test_ordering_by_position(self):

        second = Question.objects.create(
            subcategory=self.subcategory,
            code="Q2",
            question_type="text",
            description="Second",
            position=2.0,
        )

        first = Question.objects.create(
            subcategory=self.subcategory,
            code="Q0",
            question_type="text",
            description="First",
            position=0.5,
        )

        first.survey.add(self.survey)
        second.survey.add(self.survey)

        questions = list(Question.objects.all())

        self.assertEqual(questions[0], first)
        self.assertEqual(questions[1], self.question)
        self.assertEqual(questions[2], second)

    def test_update_question(self):

        self.question.description = "Updated description"
        self.question.save()

        self.question.refresh_from_db()

        self.assertEqual(
            self.question.description,
            "Updated description",
        )

    def test_delete_question(self):

        self.question.delete()

        self.assertEqual(
            Question.objects.count(),
            0,
        )
