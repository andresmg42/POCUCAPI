from django.test import TestCase

from campus.models import Campus
from observer.models import Observer
from survey.models import Survey
from surveysession.models import Surveysession
from visit.models import Visit
from visit.serializer import VisitSerializer
from zone.models import Zone


class VisitSerializerTests(TestCase):

    def setUp(self):
        self.campus = Campus.objects.create(name="Main Campus")
        self.zone = Zone.objects.create(name="Zone 1", campus=self.campus)
        self.observer = Observer.objects.create(
            name="Observer",
            email="observer@example.com",
        )
        self.survey = Survey.objects.create(
            name="Survey",
            topic="General",
            version="1.0",
            description="Survey description",
        )
        self.session = Surveysession.objects.create(
            zone=self.zone,
            observer=self.observer,
            survey=self.survey,
            url="https://example.com/session",
            number_session=1,
            observational_distance="10m",
        )
        self.visit = Visit.objects.create(
            surveysession=self.session,
            visit_number=1,
        )

    def test_serializer_contains_expected_fields(self):
        serializer = VisitSerializer(self.visit)

        self.assertEqual(
            set(serializer.data.keys()),
            {
                "id",
                "surveysession",
                "observer",
                "survey",
                "visit_number",
                "visit_start_date_time",
                "visit_end_date_time",
                "state",
            },
        )

    def test_serializer_data(self):
        serializer = VisitSerializer(self.visit)

        self.assertEqual(serializer.data["id"], self.visit.id)
        self.assertEqual(serializer.data["surveysession"], self.session.id)
        self.assertEqual(serializer.data["observer"], self.observer.name)
        self.assertEqual(serializer.data["survey"], self.survey.name)
        self.assertEqual(serializer.data["visit_number"], 1)
        self.assertEqual(serializer.data["state"], 0)

    def test_serializer_valid_data(self):
        data = {
            "surveysession": self.session.id,
        }

        serializer = VisitSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

        visit = serializer.save()

        self.assertEqual(visit.surveysession, self.session)
        self.assertEqual(visit.visit_number, 2)

    def test_serializer_missing_surveysession(self):
        serializer = VisitSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn("surveysession", serializer.errors)