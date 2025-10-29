from rest_framework import serializers
from .models import Visit
from django.db import transaction

class VisitSerializer(serializers.ModelSerializer):

    visit_number=serializers.IntegerField(read_only=True)

    class Meta:
        model=Visit
        fields=['id','surveysession','visit_number','visit_start_date_time','visit_end_date_time','state']
    
    def create(self,validated_data):
        
        with transaction.atomic():
            last_visit=Visit.objects.select_for_update().filter(surveysession=validated_data['surveysession']).order_by('-visit_number').first()

            if last_visit:
                new_number=last_visit.visit_number + 1
            else:
                new_number=1

            validated_data['visit_number'] =new_number

            return super().create(validated_data) 

            
            

            

    
        
