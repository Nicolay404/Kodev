from rest_framework import serializers
from .models import Emergency, FirstAidGuide


class FirstAidGuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirstAidGuide
        fields = ("id", "contenido", "fecha_generacion")


class EmergencySerializer(serializers.ModelSerializer):
    guides = FirstAidGuideSerializer(many=True, read_only=True)
    class Meta:
        model = Emergency
        fields = "__all__"
        read_only_fields = ("id", "patient_id", "status", "created_at")
