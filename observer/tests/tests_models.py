from django.test import TestCase
from observer.models import Observer


class ObserverModelTests(TestCase):

    def setUp(self):
        self.observer = Observer.objects.create(
            name="John Doe", email="john@example.com"
        )

    def test_create_observer(self):
        """Observer should be created correctly."""
        self.assertEqual(Observer.objects.count(), 1)

    def test_name_saved_correctly(self):
        self.assertEqual(self.observer.name, "John Doe")

    def test_email_saved_correctly(self):
        self.assertEqual(self.observer.email, "john@example.com")

    def test_register_date_is_created(self):
        """register_date should be automatically assigned."""
        self.assertIsNotNone(self.observer.register_date)

    def test_string_representation(self):
        """__str__ should return the observer's name."""
        self.assertEqual(str(self.observer), "John Doe")

    def test_update_observer(self):
        self.observer.name = "Jane Doe"
        self.observer.email = "jane@example.com"
        self.observer.save()

        self.observer.refresh_from_db()

        self.assertEqual(self.observer.name, "Jane Doe")
        self.assertEqual(self.observer.email, "jane@example.com")

    def test_multiple_observers(self):
        Observer.objects.create(name="Alice", email="alice@example.com")

        self.assertEqual(Observer.objects.count(), 2)

    def test_delete_observer(self):
        self.observer.delete()
        self.assertEqual(Observer.objects.count(), 0)
