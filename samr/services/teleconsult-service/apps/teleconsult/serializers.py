from rest_framework import serializers
from .models import TeleconsultSession


class TeleconsultSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeleconsultSession
        fields = "__all__"
        read_only_fields = ("id", "room_token", "status", "closed_at")


class TeleconsultCreateSerializer(serializers.Serializer):
    patient_id = serializers.UUIDField()
    professional_id = serializers.UUIDField(required=False)
    emergency_id = serializers.UUIDField(required=False)
