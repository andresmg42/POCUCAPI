from django.test import TestCase

from survey.models import Survey


class SurveyModelTests(TestCase):

    def setUp(self):
        self.survey = Survey.objects.create(
            name="Survey",
            topic="General",
            version="1.0",
            description="Survey description",
            image_url="https://example.com/image.png",
        )

    def test_create_survey(self):
        self.assertEqual(Survey.objects.count(), 1)

    def test_name_saved_correctly(self):
        self.assertEqual(self.survey.name, "Survey")

    def test_topic_saved_correctly(self):
        self.assertEqual(self.survey.topic, "General")

    def test_version_saved_correctly(self):
        self.assertEqual(self.survey.version, "1.0")

    def test_description_saved_correctly(self):
        self.assertEqual(self.survey.description, "Survey description")

    def test_image_url_saved_correctly(self):
        self.assertEqual(self.survey.image_url, "https://example.com/image.png")

    def test_string_representation(self):
        self.assertEqual(str(self.survey), "Survey")

    def test_update_survey(self):
        self.survey.name = "Updated Survey"
        self.survey.topic = "Updated Topic"
        self.survey.version = "2.0"
        self.survey.description = "Updated description"
        self.survey.image_url = "https://example.com/updated.png"
        self.survey.save()

        self.survey.refresh_from_db()

        self.assertEqual(self.survey.name, "Updated Survey")
        self.assertEqual(self.survey.topic, "Updated Topic")
        self.assertEqual(self.survey.version, "2.0")
        self.assertEqual(self.survey.description, "Updated description")
        self.assertEqual(self.survey.image_url, "https://example.com/updated.png")

    def test_delete_survey(self):
        self.survey.delete()

        self.assertEqual(Survey.objects.count(), 0)