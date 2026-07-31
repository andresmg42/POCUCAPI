from django.test import TestCase

from campus.models import Campus
from campus.serializer import CampusSerializer


class CampusSerializerTests(TestCase):

    def setUp(self):
        self.campus = Campus.objects.create(name="Meléndez")

    def test_serializer_contains_expected_fields(self):
        """Serializer exposes all model fields."""
        serializer = CampusSerializer()

        self.assertEqual(set(serializer.fields.keys()), {"id", "name"})

    def test_serializer_serializes_campus(self):
        """Serializer correctly converts a Campus instance into JSON data."""
        serializer = CampusSerializer(self.campus)

        self.assertEqual(
            serializer.data,
            {
                "id": self.campus.id,
                "name": "Meléndez",
            },
        )

    def test_serializer_creates_campus(self):
        """Serializer creates a Campus from valid input."""
        data = {"name": "San Fernando"}

        serializer = CampusSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

        campus = serializer.save()

        self.assertEqual(campus.name, "San Fernando")
        self.assertEqual(Campus.objects.count(), 2)

    def test_serializer_requires_name(self):
        """Name is required."""
        serializer = CampusSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_serializer_rejects_blank_name(self):
        """Blank names are not allowed."""
        serializer = CampusSerializer(data={"name": ""})

        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_serializer_rejects_duplicate_name(self):
        """Campus names must be unique."""
        serializer = CampusSerializer(data={"name": "Meléndez"})

        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_serializer_meta_model(self):
        """Serializer Meta.model is Campus."""
        self.assertEqual(CampusSerializer.Meta.model, Campus)

    def test_serializer_meta_fields(self):
        """Serializer uses all model fields."""
        self.assertEqual(CampusSerializer.Meta.fields, "__all__")
