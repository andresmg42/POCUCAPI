from django.test import TestCase

from campus.models import Campus
from zone.models import Zone
from zone.serializer import ZoneSerializer


class ZoneSerializerTests(TestCase):

    def setUp(self):
        self.campus = Campus.objects.create(name="Main Campus")
        self.zone = Zone.objects.create(
            name="Zone 1",
            campus=self.campus,
            zone_type=Zone.ZoneType.OPEN,
        )

    def test_serializer_contains_expected_fields(self):
        serializer = ZoneSerializer(self.zone)

        self.assertEqual(
            set(serializer.data.keys()),
            {"id", "name", "number", "zone_type", "campus", "campus_name"},
        )

    def test_serializer_data(self):
        serializer = ZoneSerializer(self.zone)

        self.assertEqual(serializer.data["id"], self.zone.id)
        self.assertEqual(serializer.data["name"], "Zone 1")
        self.assertEqual(serializer.data["number"], 1)
        self.assertEqual(serializer.data["zone_type"], Zone.ZoneType.OPEN)
        self.assertEqual(serializer.data["campus"], self.campus.id)
        self.assertEqual(serializer.data["campus_name"], "Main Campus")

    def test_serializer_valid_data(self):
        data = {
            "name": "Zone 2",
            "zone_type": Zone.ZoneType.CLOSED,
            "campus": self.campus.id,
        }

        serializer = ZoneSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

        zone = serializer.save()

        self.assertEqual(zone.name, "Zone 2")
        self.assertEqual(zone.zone_type, Zone.ZoneType.CLOSED)
        self.assertEqual(zone.campus, self.campus)
        self.assertEqual(zone.number, 2)

    def test_serializer_missing_name(self):
        serializer = ZoneSerializer(
            data={
                "zone_type": Zone.ZoneType.OPEN,
                "campus": self.campus.id,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_serializer_allows_missing_campus(self):
        serializer = ZoneSerializer(
            data={
                "name": "Zone 2",
                "zone_type": Zone.ZoneType.OPEN,
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)