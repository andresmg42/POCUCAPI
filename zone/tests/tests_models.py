from django.db import IntegrityError
from django.test import TestCase

from campus.models import Campus
from zone.models import Zone


class ZoneModelTests(TestCase):

    def setUp(self):
        self.campus = Campus.objects.create(name="Main Campus")
        self.zone = Zone.objects.create(
            name="Zone 1",
            campus=self.campus,
            zone_type=Zone.ZoneType.OPEN,
        )

    def test_create_zone(self):
        self.assertEqual(Zone.objects.count(), 1)

    def test_name_saved_correctly(self):
        self.assertEqual(self.zone.name, "Zone 1")

    def test_number_saved_correctly(self):
        self.assertEqual(self.zone.number, 1)

    def test_zone_type_saved_correctly(self):
        self.assertEqual(self.zone.zone_type, Zone.ZoneType.OPEN)

    def test_campus_saved_correctly(self):
        self.assertEqual(self.zone.campus, self.campus)

    def test_string_representation(self):
        self.assertEqual(str(self.zone), "Zone 1 (Espacio Abierto)")

    def test_update_zone(self):
        self.zone.name = "Updated Zone"
        self.zone.zone_type = Zone.ZoneType.CLOSED
        self.zone.save()

        self.zone.refresh_from_db()

        self.assertEqual(self.zone.name, "Updated Zone")
        self.assertEqual(self.zone.zone_type, Zone.ZoneType.CLOSED)

    def test_delete_zone(self):
        self.zone.delete()

        self.assertEqual(Zone.objects.count(), 0)

    def test_unique_number_by_campus(self):
        with self.assertRaises(IntegrityError):
            Zone.objects.create(
                name="Zone 2",
                campus=self.campus,
                number=1,
            )