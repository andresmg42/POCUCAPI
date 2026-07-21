from rest_framework import serializers
from .models import Surveysession
from .models import Surveysession, Zone, Observer, Survey
from django.utils import timezone
from visit.models import Visit
from django.db import transaction



class SurveysessionSerializer(serializers.ModelSerializer):
    
    observer = serializers.SlugRelatedField(
        queryset=Observer.objects.all(),
        slug_field='email',
        required=False
    )

    zone = serializers.PrimaryKeyRelatedField(
        queryset=Zone.objects.all()
    )

    campus_name= serializers.ReadOnlyField(source='zone.campus.name')

    
    zone_name = serializers.StringRelatedField(source='zone', read_only=True)

    
    
    survey = serializers.PrimaryKeyRelatedField(queryset=Survey.objects.all())

    number_session=serializers.IntegerField(read_only=True)

    visits_created=serializers.SerializerMethodField()

    survey_name=serializers.ReadOnlyField(source='survey.name')

    class Meta:
        model = Surveysession
        fields = [
            'id', 'zone','zone_name', 'observer', 'survey', 'number_session', 
            'start_date', 'end_date', 'observational_distance', 'url', 'uploaded_at','state','visit_number','visits_created','campus_name','survey_name'
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
    
    def create(self,validated_data):
        
        with transaction.atomic():

            survey=Survey.objects.select_for_update().get(pk=validated_data['survey'].pk)
            last_session=Surveysession.objects.filter(survey=survey,observer=validated_data['observer']).order_by('-number_session').first()

            if last_session:
                new_number=last_session.number_session + 1
            else:
                new_number=1

            validated_data['number_session'] =new_number

            return super().create(validated_data)
    
    def get_visits_created(self,obj):
        try:
            return obj.visits.count()
        except Exception as e:
            return 0
        
    def validate_visit_number(self,value):
        
        if self.instance:
            current_visits=Visit.objects.filter(surveysession_id=self.instance.id).count()
            if value < current_visits:
                raise serializers.ValidationError(f"The new visit_number must be higher than the current visit count wich is {current_visits} visits")
        
        else:
            if value < 1:
                raise serializers.ValidationError("The visit_number value must be higher or equal than 1")
        
        return value

        

class SessionReportSerializer(serializers.ModelSerializer):
    survey=serializers.PrimaryKeyRelatedField(queryset=Survey.objects.all())
    visits_rate= serializers.SerializerMethodField()
    zone_name= serializers.SerializerMethodField()
    campus_name=serializers.ReadOnlyField(source='zone.campus.name')

    class Meta:
        model=Surveysession
        fields=['id','zone','zone_name','observer','survey','uploaded_at','url','number_session','start_date','end_date','observational_distance','visits_rate','state','campus_name']

    def get_visits_rate(self,obj):

        try:
            observer_completed_visits=Visit.objects.filter(
                surveysession=obj,
                state=2
            ).count()

            
            total_session_visits=obj.visit_number

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
