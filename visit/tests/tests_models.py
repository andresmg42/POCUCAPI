from django.db import IntegrityError
from django.test import TestCase

from campus.models import Campus
from observer.models import Observer
from survey.models import Survey
from surveysession.models import Surveysession
from visit.models import Visit
from zone.models import Zone


class VisitModelTests(TestCase):

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

    def test_create_visit(self):
        self.assertEqual(Visit.objects.count(), 1)

    def test_surveysession_saved_correctly(self):
        self.assertEqual(self.visit.surveysession, self.session)

    def test_visit_number_saved_correctly(self):
        self.assertEqual(self.visit.visit_number, 1)

    def test_string_representation(self):
        self.assertEqual(
            str(self.visit),
            "Observer-Survey-session-1-visit-1",
        )

    def test_update_visit(self):
        self.visit.state = 1
        self.visit.save()

        self.visit.refresh_from_db()

        self.assertEqual(self.visit.state, 1)

    def test_delete_visit(self):
        self.visit.delete()

        self.assertEqual(Visit.objects.count(), 0)
        self.session.refresh_from_db()
        self.assertEqual(self.session.state, 1)
        self.assertIsNone(self.session.end_date)

    def test_unique_visit_number_per_session(self):
        with self.assertRaises(IntegrityError):
            Visit.objects.create(
                surveysession=self.session,
                visit_number=1,
            )