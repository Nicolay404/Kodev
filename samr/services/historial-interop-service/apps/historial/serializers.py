from rest_framework import serializers
from .models import Historial, Consentimiento

class HistorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Historial
        fields = '__all__'

class ConsentimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consentimiento
        fields = '__all__'
