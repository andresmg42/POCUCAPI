from django.test import TestCase

from observer.models import Observer
from observer.serializer import (
    ObserverSerializer,
    ObserverTableSerializer,
)


class ObserverSerializerTests(TestCase):

    def setUp(self):
        self.observer = Observer.objects.create(
            name="John Doe", email="john@example.com"
        )

    def test_observer_serializer_fields(self):
        serializer = ObserverSerializer(self.observer)

        self.assertEqual(
            serializer.data,
            {
                "id": self.observer.id,
                "name": "John Doe",
                "email": "john@example.com",
            },
        )

    def test_observer_serializer_contains_expected_fields(self):
        serializer = ObserverSerializer(self.observer)

        self.assertEqual(
            set(serializer.data.keys()),
            {"id", "name", "email"},
        )


class ObserverTableSerializerTests(TestCase):

    def setUp(self):
        self.observer = Observer.objects.create(
            name="Jane Doe", email="jane@example.com"
        )

    def test_table_serializer_without_sessions(self):
        serializer = ObserverTableSerializer(self.observer)

        self.assertEqual(serializer.data["sessions"], "0/0")
        self.assertEqual(serializer.data["completed_rate"], 0.0)

    def test_table_serializer_with_sessions(self):
        self.observer.completed_sessions = 3
        self.observer.total_sessions = 5

        serializer = ObserverTableSerializer(self.observer)

        self.assertEqual(serializer.data["sessions"], "3/5")
        self.assertEqual(serializer.data["completed_rate"], 60.0)

    def test_completed_rate_is_rounded(self):
        self.observer.completed_sessions = 2
        self.observer.total_sessions = 3

        serializer = ObserverTableSerializer(self.observer)

        self.assertEqual(serializer.data["completed_rate"], 66.67)

    def test_completed_rate_is_100(self):
        self.observer.completed_sessions = 10
        self.observer.total_sessions = 10

        serializer = ObserverTableSerializer(self.observer)

        self.assertEqual(serializer.data["completed_rate"], 100.0)

    def test_sessions_string(self):
        self.observer.completed_sessions = 7
        self.observer.total_sessions = 9

        serializer = ObserverTableSerializer(self.observer)

        self.assertEqual(serializer.data["sessions"], "7/9")

    def test_table_serializer_contains_expected_fields(self):
        serializer = ObserverTableSerializer(self.observer)

        self.assertEqual(
            set(serializer.data.keys()),
            {
                "id",
                "email",
                "name",
                "register_date",
                "sessions",
                "completed_rate",
            },
        )
