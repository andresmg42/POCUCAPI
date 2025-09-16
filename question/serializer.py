from rest_framework import serializers
from .models import Question,Question_Survey

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Question
        fields='__all__'


class QuestionSurveySerilizer(serializers.ModelSerializer):
    class Meta:
        model=Question_Survey
        fields='__all__'