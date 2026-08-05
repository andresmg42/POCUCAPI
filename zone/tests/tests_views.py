from types import SimpleNamespace
from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from campus.models import Campus
from zone.models import Zone
from zone.views import ZoneViewSet, get_zones_by_campus


class ZoneViewSetTests(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.list_view = ZoneViewSet.as_view({"get": "list", "post": "create"})
        self.detail_view = ZoneViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        )

        self.campus = Campus.objects.create(name="Main Campus")
        self.other_campus = Campus.objects.create(name="Other Campus")
        self.first = Zone.objects.create(
            name="Zone 1",
            campus=self.campus,
            number=1,
            zone_type=Zone.ZoneType.OPEN,
        )
        self.second = Zone.objects.create(
            name="Zone 2",
            campus=self.campus,
            number=2,
            zone_type=Zone.ZoneType.CLOSED,
        )

    def _identity(self, role, observer=None):
        return SimpleNamespace(
            is_authenticated=True,
            is_admin=role == "admin",
            is_staff=role == "staff",
            is_observer=role == "observer",
            role=role,
            observer=observer,
        )

    def test_list_zones_as_admin(self):
        request = self.factory.get("/zone/")

        with patch("users.permissions.resolve_request_identity", return_value=self._identity("admin")):
            response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_zone(self):
        request = self.factory.get("/zone/1/")

        with patch("users.permissions.resolve_request_identity", return_value=self._identity("admin")):
            response = self.detail_view(request, pk=self.first.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Zone 1")

    def test_create_zone(self):
        request = self.factory.post(
            "/zone/",
            {
                "name": "Zone 3",
                "zone_type": Zone.ZoneType.MIXED,
                "campus": self.campus.id,
            },
        )

        with patch("users.permissions.resolve_request_identity", return_value=self._identity("admin")):
            response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Zone.objects.count(), 3)

    def test_update_zone(self):
        request = self.factory.put(
            "/zone/1/",
            {
                "name": "Updated Zone",
                "zone_type": Zone.ZoneType.CLOSED,
                "campus": self.campus.id,
            },
        )

        with patch("users.permissions.resolve_request_identity", return_value=self._identity("admin")):
            response = self.detail_view(request, pk=self.first.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.first.refresh_from_db()

        self.assertEqual(self.first.name, "Updated Zone")
        self.assertEqual(self.first.zone_type, Zone.ZoneType.CLOSED)

    def test_delete_zone(self):
        request = self.factory.delete("/zone/1/")

        with patch("users.permissions.resolve_request_identity", return_value=self._identity("admin")):
            response = self.detail_view(request, pk=self.first.id)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Zone.objects.count(), 1)


class ZoneFunctionViewTests(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.campus = Campus.objects.create(name="Main Campus")
        self.zone = Zone.objects.create(
            name="Zone 1",
            campus=self.campus,
            number=1,
            zone_type=Zone.ZoneType.OPEN,
        )

    def test_get_zones_by_campus(self):
        request = self.factory.get(
            "/zone/get_zones_by_campus/",
            {"campus_id": self.campus.id},
        )

        response = get_zones_by_campus(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Zone 1")

    def test_get_zones_by_campus_missing_param(self):
        request = self.factory.get("/zone/get_zones_by_campus/")

        response = get_zones_by_campus(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {"message": "campus_id parameter is required"},
        )