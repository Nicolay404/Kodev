from rest_framework import serializers
from .models import Alert, VitalSign


class VitalSignSerializer(serializers.ModelSerializer):
    class Meta:
        model = VitalSign
        fields = "__all__"
        read_only_fields = ("id", "recorded_at")

    def validate_value(self, value):
        if value.get("resourceType") != "Observation" or not isinstance(value.get("measurements"), dict):
            raise serializers.ValidationError("value debe ser una Observation con measurements.")
        return value


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = "__all__"
