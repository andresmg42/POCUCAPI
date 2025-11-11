from rest_framework import serializers
from .models import Surveysession
from .models import Surveysession, Zone, Observer, Survey
from django.utils import timezone
from visit.models import Visit



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


class SessionReportSerializer(serializers.ModelSerializer):
    survey=serializers.PrimaryKeyRelatedField(queryset=Survey.objects.all())
    visits_rate= serializers.SerializerMethodField()
    zone_name= serializers.SerializerMethodField()

    class Meta:
        model=Surveysession
        fields=['id','zone','zone_name','observer','survey','uploaded_at','url','number_session','start_date','end_date','observational_distance','visits_rate','state']

    def get_visits_rate(self,obj):

        try:
            observer_completed_visits=Visit.objects.filter(
                surveysession=obj,
                state=2
            ).count()

            total_session_visits=Visit.objects.filter(surveysession=obj).count()

            if total_session_visits==0:
                return 0.0
            
            rate=f'{observer_completed_visits}/{total_session_visits}'
            return rate
        
        except Exception as e:

            return f'Error calculating rate:{e}'
        
    def get_zone_name(self,obj):
        return obj.zone.name
        


        
        

    

    












        
    # def get_state(self,obj):

    #     completed_visits_count=obj.visits.filter(state=2).count()

    #     if completed_visits_count==obj.visit_number:
    #         return 2
    #     return obj.state
