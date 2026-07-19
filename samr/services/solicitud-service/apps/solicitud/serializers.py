from rest_framework import serializers
from .models import Conversation, FAQ, Solicitud

class ChatMessageSerializer(serializers.Serializer):
    message = serializers.CharField()
    chat_id = serializers.IntegerField(required=False)

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'

class SolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solicitud
        fields = '__all__'
        read_only_fields = ('patient_id', 'estado', 'consorcio_validation_id', 'created_at', 'updated_at')
