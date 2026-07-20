from rest_framework import serializers
from .models import Patient
from .services import encrypt_cedula


class PatientSerializer(serializers.ModelSerializer):
    cedula = serializers.CharField(write_only=True, required=False, min_length=5)

    class Meta:
        model = Patient
        exclude = ("cedula_encrypted",)
        read_only_fields = ("id", "user_id")

    def validate(self, attrs):
        if self.instance is None and not attrs.get("cedula"):
            raise serializers.ValidationError({"cedula": "Este campo es obligatorio."})
        return attrs

    def create(self, validated_data):
        cedula = validated_data.pop("cedula")
        return Patient.objects.create(cedula_encrypted=encrypt_cedula(cedula), **validated_data)

    def update(self, instance, validated_data):
        cedula = validated_data.pop("cedula", None)
        if cedula:
            instance.cedula_encrypted = encrypt_cedula(cedula)
        return super().update(instance, validated_data)


class PatientSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ("id", "user_id", "blood_type", "allergies", "chronic_conditions", "latitude", "longitude", "consent_ai", "consent_sharing")
