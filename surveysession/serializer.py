from rest_framework import serializers
from .models import Surveysession
from .models import Surveysession, Zone, Observer, Survey
from django.utils import timezone


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
            'start_date', 'end_date', 'observational_distance', 'url', 'uploaded_at','state','visit_number'
        ]
        read_only_fields = ['uploaded_at']

    def update(self, instance, validated_data):

        instance=super().update(instance,validated_data)

        completed_visits_count=instance.visits.filter(state=2).count()

        if completed_visits_count == instance.visit_number and instance.state != 2:
            instance.state = 2
            instance.end_date = timezone.now() 
            instance.save(update_fields=['state', 'end_date'])

        elif completed_visits_count!=instance.visit_number and instance.state==2:
            instance.state=1
            instance.end_date=None
            instance.save(update_fields=['state','end_date'])
        return instance




    
    # def get_state(self,obj):

    #     completed_visits_count=obj.visits.filter(state=2).count()

    #     if completed_visits_count==obj.visit_number:
    #         return 2
    #     return obj.state
