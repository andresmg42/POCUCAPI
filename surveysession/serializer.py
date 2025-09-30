from rest_framework import serializers
from .models import Surveysession
from .models import Surveysession, Zone, Observer, Survey


class SurveysessionSerializer(serializers.ModelSerializer):
    # This field now accepts an email string and finds the correct Observer.
    observer = serializers.SlugRelatedField(
        queryset=Observer.objects.all(),
        slug_field='email' 
    )

    # This field now accepts a number string and finds the correct Zone.
    zone = serializers.SlugRelatedField(
        queryset=Zone.objects.all(),
        slug_field='number'
    )

    # The survey field can still use its ID.
    survey = serializers.PrimaryKeyRelatedField(queryset=Survey.objects.all())

    class Meta:
        model = Surveysession
        fields = [
            'id', 'zone', 'observer', 'survey', 'number_session', 
            'start_date', 'end_date', 'observational_distance', 'url', 'uploaded_at'
        ]
        read_only_fields = ['uploaded_at']