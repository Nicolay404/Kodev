from rest_framework import serializers
from .models import Evaluacion, Matching

class EvaluacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluacion
        fields = '__all__'
        read_only_fields = ('riesgo_score', 'recomendaciones', 'created_at', 'updated_at')

class MatchingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matching
        fields = '__all__'
