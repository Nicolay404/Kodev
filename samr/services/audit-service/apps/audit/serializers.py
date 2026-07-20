from rest_framework import serializers
from .models import DecisionIA

class DecisionIASerializer(serializers.ModelSerializer):
    class Meta:
        model = DecisionIA
        fields = '__all__'
        read_only_fields = ('solicitud_id', 'evaluacion_id', 'decision', 'context', 'created_at')
