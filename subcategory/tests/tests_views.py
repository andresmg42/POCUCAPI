from unittest.mock import patch

from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework import status

from category.models import Category
from subcategory.models import Subcategory
from subcategory.views import SubcategoryViewSet


class SubcategoryViewSetTests(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.list_view = SubcategoryViewSet.as_view({"get": "list", "post": "create"})
        self.detail_view = SubcategoryViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
            }
        )

        self.category = Category.objects.create(name="Category")

        self.first = Subcategory.objects.create(
            category=self.category,
            name="First",
        )

        self.second = Subcategory.objects.create(
            category=self.category,
            name="Second",
        )

    def test_list_subcategories(self):
        request = self.factory.get("/subcategory/")
        with patch("subcategory.views.SubcategoryPermissions.has_permission", return_value=True):
            response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_subcategory(self):
        request = self.factory.get("/subcategory/1/")
        with patch("subcategory.views.SubcategoryPermissions.has_permission", return_value=True):
            response = self.detail_view(request, pk=self.first.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "First")

    def test_create_subcategory(self):
        request = self.factory.post(
            "/subcategory/",
            {
                "category": self.category.id,
                "name": "New Subcategory",
            },
        )
        with patch("subcategory.views.SubcategoryPermissions.has_permission", return_value=True):
            response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subcategory.objects.count(), 3)

    def test_update_subcategory(self):
        request = self.factory.put(
            "/subcategory/1/",
            {
                "category": self.category.id,
                "name": "Updated",
            },
        )
        with patch("subcategory.views.SubcategoryPermissions.has_permission", return_value=True):
            response = self.detail_view(request, pk=self.first.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.first.refresh_from_db()

        self.assertEqual(self.first.name, "Updated")

    def test_delete_subcategory(self):
        request = self.factory.delete("/subcategory/1/")
        with patch("subcategory.views.SubcategoryPermissions.has_permission", return_value=True):
            response = self.detail_view(request, pk=self.first.id)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Subcategory.objects.count(), 1)