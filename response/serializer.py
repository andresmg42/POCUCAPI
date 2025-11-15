from rest_framework import serializers
from .models import Response
from .models import QuestionCommentAnswer


class ResponseSerializer(serializers.ModelSerializer):
    numeric_value = serializers.IntegerField(required=False, allow_null=True)
    class Meta:
        model=Response
        fields='__all__'
    

class QuestionCommentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model=QuestionCommentAnswer
        fields='__all__'
