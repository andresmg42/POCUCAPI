from django.db import IntegrityError
from django.test import TestCase

from campus.models import Campus
from observer.models import Observer
from survey.models import Survey
from surveysession.models import Surveysession
from zone.models import Zone


class SurveysessionModelTests(TestCase):

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

    def test_create_surveysession(self):
        self.assertEqual(Surveysession.objects.count(), 1)

    def test_zone_saved_correctly(self):
        self.assertEqual(self.session.zone, self.zone)

    def test_observer_saved_correctly(self):
        self.assertEqual(self.session.observer, self.observer)

    def test_survey_saved_correctly(self):
        self.assertEqual(self.session.survey, self.survey)

    def test_url_saved_correctly(self):
        self.assertEqual(self.session.url, "https://example.com/session")

    def test_number_session_saved_correctly(self):
        self.assertEqual(self.session.number_session, 1)

    def test_string_representation(self):
        self.assertEqual(
            str(self.session),
            "Observer-Survey-session-1",
        )

    def test_update_surveysession(self):
        self.session.url = "https://example.com/updated"
        self.session.observational_distance = "20m"
        self.session.state = 1
        self.session.save()

        self.session.refresh_from_db()

        self.assertEqual(self.session.url, "https://example.com/updated")
        self.assertEqual(self.session.observational_distance, "20m")
        self.assertEqual(self.session.state, 1)

    def test_delete_surveysession(self):
        self.session.delete()

        self.assertEqual(Surveysession.objects.count(), 0)

    def test_unique_session_constraint(self):
        with self.assertRaises(IntegrityError):
            Surveysession.objects.create(
                zone=self.zone,
                observer=self.observer,
                survey=self.survey,
                url="https://example.com/another",
                number_session=1,
                observational_distance="10m",
            )