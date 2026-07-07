from rest_framework import serializers
from .models import Zone,Campus
from django.db import transaction


class ZoneSerializer(serializers.ModelSerializer):
    campus_name=serializers.ReadOnlyField(source='campus.name')
    number = serializers.IntegerField(read_only=True)
    class Meta:
        model=Zone
        fields=['id','name','number','zone_type','campus','campus_name']

    def create(self,validated_data):

        with transaction.atomic():
            campus=Campus.objects.select_for_update().get(pk=validated_data['campus'].pk)
            last_zone=Zone.objects.filter(campus=campus).order_by('-number').first()

            if last_zone:
                new_number=last_zone.number + 1
            else:
                new_number=1

            validated_data['number']=new_number

            return super().create(validated_data)
