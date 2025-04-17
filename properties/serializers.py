from rest_framework import serializers
from .models import Property

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = ['owner', 'views_count', 'created_at']

class PropertyToggleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['is_active']
