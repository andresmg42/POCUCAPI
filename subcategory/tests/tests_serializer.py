from django.test import TestCase

from category.models import Category
from subcategory.models import Subcategory
from subcategory.serializer import SubcategorySerializer


class SubcategorySerializerTests(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Category")
        self.subcategory = Subcategory.objects.create(
            category=self.category,
            name="Subcategory",
        )

    def test_serializer_contains_expected_fields(self):
        serializer = SubcategorySerializer(self.subcategory)

        self.assertEqual(
            set(serializer.data.keys()),
            {"id", "category", "name", "category_name"},
        )

    def test_serializer_data(self):
        serializer = SubcategorySerializer(self.subcategory)

        self.assertEqual(
            serializer.data,
            {
                "id": self.subcategory.id,
                "category": self.category.id,
                "name": "Subcategory",
                "category_name": "Category",
            },
        )

    def test_serializer_valid_data(self):
        data = {
            "category": self.category.id,
            "name": "New Subcategory",
        }

        serializer = SubcategorySerializer(data=data)

        self.assertTrue(serializer.is_valid())

        subcategory = serializer.save()

        self.assertEqual(subcategory.category, self.category)
        self.assertEqual(subcategory.name, "New Subcategory")

    def test_serializer_missing_name(self):
        serializer = SubcategorySerializer(
            data={
                "category": self.category.id,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_serializer_missing_category(self):
        serializer = SubcategorySerializer(
            data={
                "name": "New Subcategory",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("category", serializer.errors)