from rest_framework import serializers
from .models import Response


class ResponseSerializer(serializers.ModelSerializer):
    numeric_value = serializers.IntegerField(required=False, allow_null=True)
    class Meta:
        model=Response
        fields='__all__'
    


