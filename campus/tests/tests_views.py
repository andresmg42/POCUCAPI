from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from campus.models import Campus


class CampusViewSetTests(APITestCase):

    def setUp(self):
        self.campus = Campus.objects.create(name="Meléndez")

        self.list_url = reverse("campus-list")
        self.detail_url = reverse(
            "campus-detail",
            kwargs={"pk": self.campus.pk},
        )

    ####################################################################
    # LIST
    ####################################################################

    @patch("users.permissions.resolve_request_identity")
    def test_list_campuses(self, mock_identity):
        mock_identity.return_value.is_authenticated = True
        mock_identity.return_value.role = "admin"

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Meléndez")

    ####################################################################
    # RETRIEVE
    ####################################################################

    @patch("users.permissions.resolve_request_identity")
    def test_retrieve_campus(self, mock_identity):
        mock_identity.return_value.is_authenticated = True
        mock_identity.return_value.role = "admin"

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.campus.id)
        self.assertEqual(response.data["name"], "Meléndez")

    ####################################################################
    # CREATE
    ####################################################################

    @patch("users.permissions.resolve_request_identity")
    def test_create_campus(self, mock_identity):
        mock_identity.return_value.is_authenticated = True
        mock_identity.return_value.role = "admin"

        response = self.client.post(
            self.list_url,
            {"name": "San Fernando"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Campus.objects.count(), 2)

        campus = Campus.objects.get(name="San Fernando")
        self.assertEqual(campus.name, "San Fernando")

    ####################################################################
    # UPDATE
    ####################################################################

    @patch("users.permissions.resolve_request_identity")
    def test_update_campus(self, mock_identity):
        mock_identity.return_value.is_authenticated = True
        mock_identity.return_value.role = "admin"

        response = self.client.put(
            self.detail_url,
            {"name": "Updated Campus"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.campus.refresh_from_db()
        self.assertEqual(self.campus.name, "Updated Campus")

    ####################################################################
    # DELETE
    ####################################################################

    @patch("users.permissions.resolve_request_identity")
    def test_delete_campus(self, mock_identity):
        mock_identity.return_value.is_authenticated = True
        mock_identity.return_value.role = "admin"

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Campus.objects.filter(pk=self.campus.pk).exists())
