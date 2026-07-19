from rest_framework import serializers
from .models import IoTReading, Alert

class IoTReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = IoTReading
        fields = '__all__'

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = '__all__'
