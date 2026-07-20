from rest_framework import serializers
from .models import Caso


class CasoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Caso
        fields = "__all__"
        read_only_fields = ("id", "integrity_hash", "status", "closed_at")


class CloseCaseSerializer(serializers.Serializer):
    clinical_notes = serializers.CharField()
