from rest_framework import serializers
from .models import AuditLog, AuditReview


class AuditLogSerializer(serializers.ModelSerializer):
    review = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    class Meta: model = AuditLog; fields = "__all__"
    def get_review(self, obj):
        review = AuditReview.objects.filter(audit_log_id=obj.id).order_by("-created_at").first()
        return AuditReviewSerializer(review).data if review else None
    def get_reviews(self, obj):
        reviews = AuditReview.objects.filter(audit_log_id=obj.id).order_by("created_at")
        return AuditReviewSerializer(reviews, many=True).data


class AuditReviewSerializer(serializers.ModelSerializer):
    class Meta: model = AuditReview; fields = "__all__"; read_only_fields = ("id", "audit_log_id", "revisado_por", "fecha_revision", "created_at")


class ReviewRequestSerializer(serializers.Serializer):
    estado_revision = serializers.ChoiceField(choices=("revisado", "observado"))
    comentario = serializers.CharField(required=False, allow_blank=True)
