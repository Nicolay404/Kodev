from rest_framework import serializers
from .models import Caso

class CasoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Caso
        fields = '__all__'
        read_only_fields = ('status', 'closed_at', 'created_at')
