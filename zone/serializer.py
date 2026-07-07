from rest_framework import serializers
from .models import Zone

class ZoneSerializer(serializers.ModelSerializer):
    campus=serializers.ReadOnlyField(source='campus.name')
    class Meta:
        model=Zone
        fields=['id','name','number','zone_type','campus']