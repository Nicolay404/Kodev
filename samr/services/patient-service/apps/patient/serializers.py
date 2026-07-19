from rest_framework import serializers
from .models import Patient, PatientMedicalHistory

class PatientMedicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientMedicalHistory
        fields = '__all__'

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ('user_id', 'created_at', 'updated_at')

class PatientSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('id', 'user_id', 'full_name', 'age', 'gender', 'allergies', 'chronic_conditions')
