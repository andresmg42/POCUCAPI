from django.db import IntegrityError
from django.test import TestCase

from option.models import Option


class OptionModelTests(TestCase):

    def setUp(self):
        self.numeric_option = Option.objects.create(
            description="Yes",
            type=Option.InputType.NUMERIC,
        )

    def test_create_option(self):
        """An option should be created successfully."""
        self.assertEqual(Option.objects.count(), 1)

    def test_description_saved_correctly(self):
        self.assertEqual(self.numeric_option.description, "Yes")

    def test_type_saved_correctly(self):
        self.assertEqual(self.numeric_option.type, Option.InputType.NUMERIC)

    def test_default_type_is_numeric(self):
        option = Option.objects.create(description="No")

        self.assertEqual(option.type, Option.InputType.NUMERIC)

    def test_string_representation(self):
        self.assertEqual(str(self.numeric_option), "Yes")

    def test_update_option(self):
        self.numeric_option.description = "Maybe"
        self.numeric_option.type = Option.InputType.TEXT
        self.numeric_option.save()

        self.numeric_option.refresh_from_db()

        self.assertEqual(self.numeric_option.description, "Maybe")

        self.assertEqual(self.numeric_option.type, Option.InputType.TEXT)

    def test_delete_option(self):
        self.numeric_option.delete()

        self.assertEqual(Option.objects.count(), 0)

    def test_same_description_different_type_is_allowed(self):
        Option.objects.create(
            description="Yes",
            type=Option.InputType.TEXT,
        )

        self.assertEqual(Option.objects.count(), 2)

    def test_duplicate_description_and_type_not_allowed(self):
        with self.assertRaises(IntegrityError):
            Option.objects.create(
                description="Yes",
                type=Option.InputType.NUMERIC,
            )
