from rest_framework import serializers
from category.models import Category

class CategorySerialier(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields='__all__'

