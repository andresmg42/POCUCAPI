from django.test import TestCase

from campus.models import Campus
from observer.models import Observer
from survey.models import Survey
from surveysession.models import Surveysession
from surveysession.serializer import SurveysessionSerializer
from zone.models import Zone


class SurveysessionSerializerTests(TestCase):

    def setUp(self):
        self.campus = Campus.objects.create(name="Main Campus")
        self.zone = Zone.objects.create(
            name="Zone 1",
            campus=self.campus,
        )
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

    def test_serializer_contains_expected_fields(self):
        serializer = SurveysessionSerializer(self.session)

        self.assertEqual(
            set(serializer.data.keys()),
            {
                "id",
                "zone",
                "zone_name",
                "observer",
                "survey",
                "number_session",
                "start_date",
                "end_date",
                "observational_distance",
                "url",
                "uploaded_at",
                "state",
                "visit_number",
                "visits_created",
                "campus_name",
                "survey_name",
            },
        )

    def test_serializer_data(self):
        serializer = SurveysessionSerializer(self.session)

        self.assertEqual(serializer.data["id"], self.session.id)
        self.assertEqual(serializer.data["zone"], self.zone.id)
        self.assertEqual(serializer.data["zone_name"], str(self.zone))
        self.assertEqual(serializer.data["observer"], self.observer.email)
        self.assertEqual(serializer.data["survey"], self.survey.id)
        self.assertEqual(serializer.data["number_session"], 1)
        self.assertEqual(serializer.data["observational_distance"], "10m")
        self.assertEqual(serializer.data["url"], "https://example.com/session")
        self.assertEqual(serializer.data["state"], 0)
        self.assertEqual(serializer.data["visit_number"], 6)
        self.assertEqual(serializer.data["visits_created"], 0)
        self.assertEqual(serializer.data["campus_name"], "Main Campus")
        self.assertEqual(serializer.data["survey_name"], "Survey")

    def test_serializer_valid_data(self):
        data = {
            "zone": self.zone.id,
            "observer": self.observer.email,
            "survey": self.survey.id,
            "observational_distance": "20m",
            "url": "https://example.com/new-session",
            "visit_number": 4,
        }

        serializer = SurveysessionSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

        session = serializer.save()

        self.assertEqual(session.zone, self.zone)
        self.assertEqual(session.observer, self.observer)
        self.assertEqual(session.survey, self.survey)
        self.assertEqual(session.number_session, 2)
        self.assertEqual(session.observational_distance, "20m")
        self.assertEqual(session.url, "https://example.com/new-session")
        self.assertEqual(session.visit_number, 4)

    def test_serializer_missing_zone(self):
        serializer = SurveysessionSerializer(
            data={
                "observer": self.observer.email,
                "survey": self.survey.id,
                "observational_distance": "20m",
                "url": "https://example.com/new-session",
                "visit_number": 4,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("zone", serializer.errors)

    def test_serializer_missing_survey(self):
        serializer = SurveysessionSerializer(
            data={
                "zone": self.zone.id,
                "observer": self.observer.email,
                "observational_distance": "20m",
                "url": "https://example.com/new-session",
                "visit_number": 4,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("survey", serializer.errors)

    def test_serializer_invalid_visit_number(self):
        serializer = SurveysessionSerializer(
            data={
                "zone": self.zone.id,
                "observer": self.observer.email,
                "survey": self.survey.id,
                "observational_distance": "20m",
                "url": "https://example.com/new-session",
                "visit_number": 0,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("visit_number", serializer.errors)