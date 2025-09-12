from rest_framework import serializers
from .models import Surveysession

class SurveysessionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Surveysession
        fields='__all__'