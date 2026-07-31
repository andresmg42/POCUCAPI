from django.test import TestCase

from option.models import Option
from option.serailizer import OptionSerializer


class OptionSerializerTests(TestCase):

    def setUp(self):
        self.option = Option.objects.create(
            description="Yes",
            type=Option.InputType.NUMERIC,
        )

    def test_serializer_contains_expected_fields(self):
        serializer = OptionSerializer(self.option)

        self.assertEqual(
            set(serializer.data.keys()),
            {"id", "description", "type"},
        )

    def test_serializer_data(self):
        serializer = OptionSerializer(self.option)

        self.assertEqual(
            serializer.data,
            {
                "id": self.option.id,
                "description": "Yes",
                "type": Option.InputType.NUMERIC,
            },
        )

    def test_serializer_valid_data(self):
        data = {
            "description": "No",
            "type": Option.InputType.TEXT,
        }

        serializer = OptionSerializer(data=data)

        self.assertTrue(serializer.is_valid())

        option = serializer.save()

        self.assertEqual(option.description, "No")
        self.assertEqual(option.type, Option.InputType.TEXT)

    def test_serializer_default_type(self):
        serializer = OptionSerializer(
            data={
                "description": "Maybe",
            }
        )

        self.assertTrue(serializer.is_valid())

        option = serializer.save()

        self.assertEqual(
            option.type,
            Option.InputType.NUMERIC,
        )

    def test_serializer_missing_description(self):
        serializer = OptionSerializer(
            data={
                "type": Option.InputType.NUMERIC,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("description", serializer.errors)

    def test_serializer_invalid_type(self):
        serializer = OptionSerializer(
            data={
                "description": "Yes",
                "type": "INVALID",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("type", serializer.errors)
