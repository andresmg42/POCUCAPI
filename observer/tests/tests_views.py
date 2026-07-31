from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from observer.models import Observer


class ObserverViewSetTests(APITestCase):

    def setUp(self):
        self.list_url = reverse("observer-list")

        self.observer = Observer.objects.create(
            name="John Doe",
            email="john@test.com",
        )

    @patch("users.permissions.ObserverPermission.has_permission", return_value=True)
    def test_list_observers(self, mock_permission):

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "John Doe")

    @patch("users.permissions.ObserverPermission.has_permission", return_value=True)
    def test_retrieve_observer(self, mock_permission):

        url = reverse("observer-detail", args=[self.observer.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "john@test.com")

    @patch("users.permissions.ObserverPermission.has_permission", return_value=True)
    def test_create_observer(self, mock_permission):

        response = self.client.post(
            self.list_url,
            {
                "name": "Jane Doe",
                "email": "jane@test.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Observer.objects.count(), 2)

    @patch("users.permissions.ObserverPermission.has_permission", return_value=True)
    def test_update_observer(self, mock_permission):

        url = reverse("observer-detail", args=[self.observer.id])

        response = self.client.put(
            url,
            {
                "name": "Updated Name",
                "email": "updated@test.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.observer.refresh_from_db()

        self.assertEqual(self.observer.name, "Updated Name")
        self.assertEqual(self.observer.email, "updated@test.com")

    @patch("users.permissions.ObserverPermission.has_permission", return_value=True)
    def test_partial_update_observer(self, mock_permission):

        url = reverse("observer-detail", args=[self.observer.id])

        response = self.client.patch(
            url,
            {
                "name": "Patched Name",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.observer.refresh_from_db()

        self.assertEqual(self.observer.name, "Patched Name")
        self.assertEqual(self.observer.email, "john@test.com")

    @patch("users.permissions.ObserverPermission.has_permission", return_value=True)
    def test_delete_observer(self, mock_permission):

        url = reverse("observer-detail", args=[self.observer.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Observer.objects.count(), 0)
