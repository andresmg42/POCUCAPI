from rest_framework import serializers
from .models import Observer

class ObserverSerializer(serializers.ModelSerializer):
    class Meta:
        model=Observer
        fields=['id','name','email']


class ObserverTableSerializer(serializers.ModelSerializer):
    sessions=serializers.SerializerMethodField()
    completed_rate=serializers.SerializerMethodField()

    class Meta:
        model=Observer
        fields=['id','email','name','register_date','sessions','completed_rate']
    
    def get_sessions(self,obj):
        completed= getattr(obj,'completed_sessions',0)
        total=getattr(obj,'total_sessions',0)
        return f'{completed}/{total}'
    
    def get_completed_rate(self,obj):
        completed=getattr(obj,'completed_sessions',0)
        total=getattr(obj,'total_sessions',0)
        if total==0:
            return 0.0
        return round((completed/total)*100,2)
    
    