from django.test import TestCase

from survey.models import Survey
from survey.serializer import SurveySerializer


class SurveySerializerTests(TestCase):

    def setUp(self):
        self.survey = Survey.objects.create(
            name="Survey",
            topic="General",
            version="1.0",
            description="Survey description",
            image_url="https://example.com/image.png",
        )

    def test_serializer_contains_expected_fields(self):
        serializer = SurveySerializer(self.survey)

        self.assertEqual(
            set(serializer.data.keys()),
            {"id", "name", "topic", "version", "description", "image_url", "uploaded_at"},
        )

    def test_serializer_data(self):
        serializer = SurveySerializer(self.survey)

        self.assertEqual(
            serializer.data["id"], self.survey.id,
        )
        self.assertEqual(serializer.data["name"], "Survey")
        self.assertEqual(serializer.data["topic"], "General")
        self.assertEqual(serializer.data["version"], "1.0")
        self.assertEqual(serializer.data["description"], "Survey description")
        self.assertEqual(serializer.data["image_url"], "https://example.com/image.png")

    def test_serializer_valid_data(self):
        data = {
            "name": "New Survey",
            "topic": "General",
            "version": "1.0",
            "description": "New survey description",
            "image_url": "https://example.com/new.png",
        }

        serializer = SurveySerializer(data=data)

        self.assertTrue(serializer.is_valid())

        survey = serializer.save()

        self.assertEqual(survey.name, "New Survey")
        self.assertEqual(survey.topic, "General")
        self.assertEqual(survey.version, "1.0")
        self.assertEqual(survey.description, "New survey description")
        self.assertEqual(survey.image_url, "https://example.com/new.png")

    def test_serializer_missing_name(self):
        serializer = SurveySerializer(
            data={
                "topic": "General",
                "version": "1.0",
                "description": "Survey description",
                "image_url": "https://example.com/image.png",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_serializer_missing_topic(self):
        serializer = SurveySerializer(
            data={
                "name": "Survey",
                "version": "1.0",
                "description": "Survey description",
                "image_url": "https://example.com/image.png",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("topic", serializer.errors)

    def test_serializer_missing_version(self):
        serializer = SurveySerializer(
            data={
                "name": "Survey",
                "topic": "General",
                "description": "Survey description",
                "image_url": "https://example.com/image.png",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("version", serializer.errors)

    def test_serializer_missing_description(self):
        serializer = SurveySerializer(
            data={
                "name": "Survey",
                "topic": "General",
                "version": "1.0",
                "image_url": "https://example.com/image.png",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("description", serializer.errors)