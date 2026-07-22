from rest_framework import serializers
from .models import AvailableCenterCache, Evaluacion, Matching


class EvaluacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluacion
        fields = "__all__"


class MatchingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matching
        fields = "__all__"
        read_only_fields = ("id", "evaluacion", "center_id", "score")


class MatchingRequestSerializer(serializers.Serializer):
    professional_id = serializers.UUIDField(required=False)
    patient_id = serializers.UUIDField()
    center_id = serializers.UUIDField(required=False)


class AvailableCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableCenterCache
        fields = "__all__"
