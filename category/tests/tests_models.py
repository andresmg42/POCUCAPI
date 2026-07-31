from django.test import TestCase
from category.models import Category
from zone.models import Zone


class CategoryModelTests(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name="Deportes",
            image="deportes.png",
            target_zone_type=Zone.ZoneType.OPEN,
        )

    def test_category_creation(self):
        """Category is created with the expected fields."""
        self.assertEqual(self.category.name, "Deportes")
        self.assertEqual(self.category.image, "deportes.png")
        self.assertEqual(self.category.target_zone_type, "OP")
        self.assertIsInstance(self.category, Category)

    def test_str_representation(self):
        """__str__ returns the category name."""
        self.assertEqual(str(self.category), "Deportes")

    def test_name_max_length(self):
        """The name field respects max_length=100."""
        max_length = Category._meta.get_field("name").max_length
        self.assertEqual(max_length, 100)

    def test_image_max_length(self):
        """The image field respects max_length=200."""
        max_length = Category._meta.get_field("image").max_length
        self.assertEqual(max_length, 200)

    def test_image_can_be_null(self):
        """image field allows null values."""
        category = Category.objects.create(name="Cultura", image=None)
        self.assertIsNone(category.image)

    def test_target_zone_type_can_be_null(self):
        """target_zone_type allows null (applies to any zone type)."""
        category = Category.objects.create(name="General", target_zone_type=None)
        self.assertIsNone(category.target_zone_type)

    def test_target_zone_type_can_be_blank(self):
        """target_zone_type allows blank at the validation level."""
        category = Category(name="General", target_zone_type="")
        category.full_clean()  # should not raise, since blank=True

    def test_target_zone_type_accepts_open(self):
        category = Category.objects.create(
            name="Parques", target_zone_type=Zone.ZoneType.OPEN
        )
        self.assertEqual(category.target_zone_type, "OP")

    def test_target_zone_type_accepts_closed(self):
        category = Category.objects.create(
            name="Salones", target_zone_type=Zone.ZoneType.CLOSED
        )
        self.assertEqual(category.target_zone_type, "CL")

    def test_target_zone_type_accepts_mixed(self):
        category = Category.objects.create(
            name="Patios", target_zone_type=Zone.ZoneType.MIXED
        )
        self.assertEqual(category.target_zone_type, "MX")

    def test_target_zone_type_invalid_choice_fails_validation(self):
        """An invalid target_zone_type should fail full_clean validation."""
        category = Category(name="Inválida", target_zone_type="ZZ")
        with self.assertRaises(Exception):
            category.full_clean()

    def test_name_field_required(self):
        """A blank name should fail full_clean validation."""
        category = Category(name="")
        with self.assertRaises(Exception):
            category.full_clean()

    def test_category_without_target_zone_type_applies_to_any_zone(self):
        """Business rule: no target_zone_type means applicable to any zone."""
        category = Category.objects.create(name="Todas")
        self.assertIsNone(category.target_zone_type)

    def test_category_count(self):
        """Confirm setUp created exactly one category."""
        self.assertEqual(Category.objects.count(), 1)
