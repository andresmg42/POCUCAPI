from django.test import TestCase

from category.models import Category
from option.models import Option
from question.models import Question
from question.serializer import (
    QuestionSerializer,
    QuestionSerializer2,
    QuestionSerializerSimple,
)
from subcategory.models import Subcategory
from survey.models import Survey
from zone.models import Zone


class QuestionSerializerTests(TestCase):

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

        self.option = Option.objects.create(
            description="Yes",
            type=Option.InputType.NUMERIC,
        )

        self.parent = Question.objects.create(
            subcategory=self.subcategory,
            code="Q1",
            question_type="single",
            description="Parent question",
        )

        self.parent.survey.add(self.survey)
        self.parent.options.add(self.option)

        self.child = Question.objects.create(
            subcategory=self.subcategory,
            code="Q2",
            question_type="single",
            description="Child question",
            parent_question=self.parent,
        )

        self.child.survey.add(self.survey)

    # ---------- QuestionSerializerSimple ----------

    def test_simple_serializer_fields(self):

        serializer = QuestionSerializerSimple(self.parent)

        self.assertEqual(
            serializer.data["subcategory_name"],
            "Doors",
        )

        self.assertEqual(
            serializer.data["code"],
            "Q1",
        )

    def test_simple_serializer_contains_all_fields(self):

        serializer = QuestionSerializerSimple(self.parent)

        self.assertIn("id", serializer.data)
        self.assertIn("subcategory", serializer.data)
        self.assertIn("subcategory_name", serializer.data)
        self.assertIn("description", serializer.data)

    # ---------- QuestionSerializer ----------

    def test_nested_option_serializer(self):

        serializer = QuestionSerializer(
            self.parent,
            context={"all_questions": Question.objects.all()},
        )

        self.assertEqual(
            len(serializer.data["options"]),
            1,
        )

        self.assertEqual(
            serializer.data["options"][0]["description"],
            "Yes",
        )

    def test_nested_subcategory_serializer(self):

        serializer = QuestionSerializer(
            self.parent,
            context={"all_questions": Question.objects.all()},
        )

        self.assertEqual(
            serializer.data["subcategory"]["name"],
            "Doors",
        )

    def test_sub_questions(self):

        serializer = QuestionSerializer(
            self.parent,
            context={"all_questions": Question.objects.all()},
        )

        self.assertEqual(
            len(serializer.data["sub_questions"]),
            1,
        )

        self.assertEqual(
            serializer.data["sub_questions"][0]["code"],
            "Q2",
        )

    def test_question_without_children(self):

        serializer = QuestionSerializer(
            self.child,
            context={"all_questions": Question.objects.all()},
        )

        self.assertEqual(
            serializer.data["sub_questions"],
            [],
        )

    def test_serializer_contains_expected_fields(self):

        serializer = QuestionSerializer(
            self.parent,
            context={"all_questions": Question.objects.all()},
        )

        expected = {
            "id",
            "subcategory",
            "code",
            "question_type",
            "description",
            "parent_question",
            "survey",
            "options",
            "position",
            "sub_questions",
            "is_required",
            "input_type",
        }

        self.assertEqual(
            set(serializer.data.keys()),
            expected,
        )

    # ---------- QuestionSerializer2 ----------

    def test_serializer2_fields(self):

        serializer = QuestionSerializer2(self.parent)

        self.assertEqual(
            serializer.data["code"],
            "Q1",
        )

        self.assertEqual(
            serializer.data["description"],
            "Parent question",
        )

    def test_serializer2_contains_all_fields(self):

        serializer = QuestionSerializer2(self.parent)

        self.assertIn("id", serializer.data)
        self.assertIn("subcategory", serializer.data)
        self.assertIn("survey", serializer.data)
        self.assertIn("options", serializer.data)
