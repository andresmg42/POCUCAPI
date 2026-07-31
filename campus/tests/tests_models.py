from django.test import TestCase
from django.db.utils import IntegrityError
from campus.models import Campus


class CampusModelTests(TestCase):

    def setUp(self):
        self.campus = Campus.objects.create(name="Meléndez")

    def test_campus_creation(self):
        """Campus is created with the expected name."""
        self.assertEqual(self.campus.name, "Meléndez")
        self.assertIsInstance(self.campus, Campus)

    def test_str_representation(self):
        """__str__ returns the campus name."""
        self.assertEqual(str(self.campus), "Meléndez")

    def test_name_is_unique(self):
        """Creating a second campus with the same name raises IntegrityError."""
        with self.assertRaises(IntegrityError):
            Campus.objects.create(name="Meléndez")

    def test_name_max_length(self):
        """The name field respects the max_length=100 constraint at the field level."""
        max_length = Campus._meta.get_field("name").max_length
        self.assertEqual(max_length, 100)

    def test_name_field_required(self):
        """A blank name should fail full_clean validation (CharField has blank=False by default)."""
        campus = Campus(name="")
        with self.assertRaises(Exception):
            campus.full_clean()

    def test_campus_count(self):
        """Confirm setUp created exactly one campus."""
        self.assertEqual(Campus.objects.count(), 1)

    def test_query_by_name(self):
        """Campus can be retrieved by its name."""
        fetched = Campus.objects.get(name="Meléndez")
        self.assertEqual(fetched.pk, self.campus.pk)
