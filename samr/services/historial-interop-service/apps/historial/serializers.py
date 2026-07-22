from rest_framework import serializers
from .models import Historial


class HistorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Historial
        fields = "__all__"


class ClinicalNoteSerializer(serializers.Serializer):
    note = serializers.CharField(max_length=10000, allow_blank=False, trim_whitespace=True)
