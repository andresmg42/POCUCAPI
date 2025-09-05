from rest_framework import serializers
from .models import Survey

class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model=Survey
        fields=['id','created_at','url','survey_number','start_date','end_date','observational_distance']