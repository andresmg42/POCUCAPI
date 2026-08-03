from django.test import TestCase

from category.models import Category
from subcategory.models import Subcategory


class SubcategoryModelTests(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Category")
        self.subcategory = Subcategory.objects.create(
            category=self.category,
            name="Subcategory",
        )

    def test_create_subcategory(self):
        self.assertEqual(Subcategory.objects.count(), 1)

    def test_category_saved_correctly(self):
        self.assertEqual(self.subcategory.category, self.category)

    def test_name_saved_correctly(self):
        self.assertEqual(self.subcategory.name, "Subcategory")

    def test_string_representation(self):
        self.assertEqual(str(self.subcategory), "Subcategory")

    def test_update_subcategory(self):
        self.subcategory.name = "Updated Subcategory"
        self.subcategory.save()

        self.subcategory.refresh_from_db()

        self.assertEqual(self.subcategory.name, "Updated Subcategory")

    def test_delete_subcategory(self):
        self.subcategory.delete()

        self.assertEqual(Subcategory.objects.count(), 0)