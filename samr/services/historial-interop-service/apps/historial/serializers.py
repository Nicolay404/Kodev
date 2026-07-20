from rest_framework import serializers
from .models import Historial


class HistorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Historial
        fields = "__all__"
