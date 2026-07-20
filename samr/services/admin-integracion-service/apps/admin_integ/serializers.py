from rest_framework import serializers
from .models import Center, Device


class CenterSerializer(serializers.ModelSerializer):
    class Meta: model = Center; fields = "__all__"


class CenterRegisterSerializer(serializers.ModelSerializer):
    license_number = serializers.CharField(write_only=True)
    specialties = serializers.ListField(child=serializers.CharField(), write_only=True)
    class Meta: model = Center; fields = ("name", "type", "latitude", "longitude", "license_number", "specialties")


class DeviceSerializer(serializers.ModelSerializer):
    class Meta: model = Device; fields = "__all__"


class DeviceRegisterSerializer(serializers.Serializer):
    patient_id = serializers.UUIDField(); device_type = serializers.CharField(max_length=50); serial_number = serializers.CharField(max_length=255)
