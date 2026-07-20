from rest_framework import serializers
from .models import Emergency

class EmergencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Emergency
        fields = '__all__'
        read_only_fields = ('patient_id', 'status', 'reported_at', 'dispatched_at')
