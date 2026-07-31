from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from option.models import Option


class OptionViewSetTests(APITestCase):

    def setUp(self):
        self.list_url = reverse("options-list")

        self.numeric = Option.objects.create(
            description="One",
            type=Option.InputType.NUMERIC,
        )

        self.text = Option.objects.create(
            description="Text",
            type=Option.InputType.TEXT,
        )

    @patch(
        "users.permissions.OptionPermissions.has_permission",
        return_value=True,
    )
    def test_list_options(self, mock_permission):

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    @patch(
        "users.permissions.OptionPermissions.has_permission",
        return_value=True,
    )
    def test_filter_numeric_options(self, mock_permission):

        response = self.client.get(
            self.list_url,
            {"matching_type": Option.InputType.NUMERIC},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["description"],
            "One",
        )

    @patch(
        "users.permissions.OptionPermissions.has_permission",
        return_value=True,
    )
    def test_filter_text_options(self, mock_permission):

        response = self.client.get(
            self.list_url,
            {"matching_type": Option.InputType.TEXT},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["description"],
            "Text",
        )

    @patch(
        "users.permissions.OptionPermissions.has_permission",
        return_value=True,
    )
    def test_retrieve_option(self, mock_permission):

        response = self.client.get(reverse("options-detail", args=[self.numeric.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["description"],
            "One",
        )

    @patch(
        "users.permissions.OptionPermissions.has_permission",
        return_value=True,
    )
    def test_create_option(self, mock_permission):

        response = self.client.post(
            self.list_url,
            {
                "description": "New Option",
                "type": Option.InputType.TEXT,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Option.objects.count(), 3)

    @patch(
        "users.permissions.OptionPermissions.has_permission",
        return_value=True,
    )
    def test_update_option(self, mock_permission):

        response = self.client.put(
            reverse("options-detail", args=[self.numeric.id]),
            {
                "description": "Updated",
                "type": Option.InputType.TEXT,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.numeric.refresh_from_db()

        self.assertEqual(self.numeric.description, "Updated")
        self.assertEqual(self.numeric.type, Option.InputType.TEXT)

    @patch(
        "users.permissions.OptionPermissions.has_permission",
        return_value=True,
    )
    def test_delete_option(self, mock_permission):

        response = self.client.delete(reverse("options-detail", args=[self.numeric.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Option.objects.count(), 1)
