from rest_framework import serializers
from .models import Survey

class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model=Survey
        fields=['id','name','topic','version','description','image_url']