from rest_framework import serializers
from .models.models import JsonModel

class JsonModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = JsonModel
        fields = '__all__'
