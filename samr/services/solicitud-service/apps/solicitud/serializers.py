from rest_framework import serializers
from .models import Conversation, FAQ, Solicitud


class ChatMessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000)
    chat_id = serializers.UUIDField(required=False)


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = "__all__"
        read_only_fields = ("id", "updated_at")


class SolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solicitud
        fields = "__all__"
        read_only_fields = ("id", "patient_id", "estado", "created_at")

    def validate_sintomas(self, value):
        if not value or not all(isinstance(item, str) and item.strip() for item in value):
            raise serializers.ValidationError("Debe incluir al menos un síntoma válido.")
        return value
