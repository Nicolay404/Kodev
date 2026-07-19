from rest_framework import serializers
from .models import TeleconsultSession

class TeleconsultSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeleconsultSession
        fields = '__all__'
        read_only_fields = ('room_token', 'started_at', 'ended_at')
