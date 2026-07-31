from django.test import TestCase
from category.serializer import CategorySerializer
from category.models import Category
from zone.models import Zone


class CategorySerializerTests(TestCase):

    def setUp(self):
        self.valid_data = {
            "name": "Deportes",
            "image": "deportes.png",
            "target_zone_type": Zone.ZoneType.OPEN,
        }
        self.category = Category.objects.create(**self.valid_data)

    # ---- Serialization (model -> dict) ----

    def test_serialization_contains_expected_fields(self):
        """Serialized output includes id, name, image, target_zone_type."""
        serializer = CategorySerializer(instance=self.category)
        data = serializer.data
        self.assertEqual(set(data.keys()), {"id", "name", "image", "target_zone_type"})

    def test_serialization_values_match_instance(self):
        """Serialized values match the model instance."""
        serializer = CategorySerializer(instance=self.category)
        data = serializer.data
        self.assertEqual(data["name"], "Deportes")
        self.assertEqual(data["image"], "deportes.png")
        self.assertEqual(data["target_zone_type"], "OP")

    # ---- Deserialization / validation (dict -> model) ----

    def test_valid_data_is_valid(self):
        """A well-formed payload passes validation."""
        serializer = CategorySerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_create_via_serializer(self):
        """save() creates a Category instance correctly."""
        data = {
            "name": "Cultura",
            "image": "cultura.png",
            "target_zone_type": Zone.ZoneType.CLOSED,
        }
        serializer = CategorySerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        category = serializer.save()
        self.assertEqual(category.name, "Cultura")
        self.assertEqual(category.target_zone_type, "CL")
        self.assertEqual(Category.objects.count(), 2)  # setUp + this one

    def test_missing_name_is_invalid(self):
        """name is required — missing it should fail validation."""
        data = {"image": "x.png", "target_zone_type": Zone.ZoneType.OPEN}
        serializer = CategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_blank_name_is_invalid(self):
        """An empty name string should fail validation."""
        data = {"name": "", "image": "x.png", "target_zone_type": Zone.ZoneType.OPEN}
        serializer = CategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_image_can_be_omitted(self):
        """image is optional (blank=True), omitting it should still validate."""
        data = {"name": "Sin Imagen", "target_zone_type": Zone.ZoneType.OPEN}
        serializer = CategorySerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_target_zone_type_can_be_omitted(self):
        """target_zone_type is optional, omitting it should still validate."""
        data = {"name": "General", "image": "x.png"}
        serializer = CategorySerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_target_zone_type_choice_rejected(self):
        """An out-of-choices target_zone_type should fail validation."""
        data = {"name": "Inválida", "image": "x.png", "target_zone_type": "ZZ"}
        serializer = CategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("target_zone_type", serializer.errors)

    def test_name_max_length_enforced(self):
        """A name over 100 characters should fail validation."""
        data = {
            "name": "A" * 101,
            "image": "x.png",
            "target_zone_type": Zone.ZoneType.OPEN,
        }
        serializer = CategorySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    # ---- Update ----

    def test_update_via_serializer(self):
        """Partial update changes only the targeted field."""
        serializer = CategorySerializer(
            instance=self.category,
            data={"name": "Deportes Actualizado"},
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.name, "Deportes Actualizado")
        self.assertEqual(updated.target_zone_type, "OP")  # unchanged
