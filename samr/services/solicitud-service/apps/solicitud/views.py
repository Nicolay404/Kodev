from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from events.publisher import publicar_evento
from tasks.validate_with_consortium import validate_with_consortium
from .models import Conversation, FAQ
from .permissions import IsAdminUser
from .serializers import ChatMessageSerializer, FAQSerializer, SolicitudSerializer
from .services import get_chat_adapter


class PatientOnlyMixin:
    def ensure_patient(self, request):
        return request.user.rol == "patient"


class ChatView(PatientOnlyMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not self.ensure_patient(request):
            return Response({"error": "Acceso exclusivo para pacientes"}, status=403)
        serializer = ChatMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chat_id = serializer.validated_data.get("chat_id")
        if chat_id:
            conversation = Conversation.objects.filter(id=chat_id, patient_id=request.user.id).first()
            if not conversation:
                return Response({"error": "Conversación no encontrada"}, status=404)
        else:
            conversation = Conversation.objects.create(patient_id=request.user.id)
        now = timezone.now().isoformat()
        message = serializer.validated_data["message"]
        conversation.messages.append({"role": "user", "content": message, "timestamp": now})
        result = get_chat_adapter().respond(message)
        response_time = timezone.now().isoformat()
        conversation.messages.append({"role": "assistant", "content": result.text, "timestamp": response_time, "source": result.source, "confidence": result.confidence})
        conversation.save(update_fields=["messages"])
        publicar_evento("ai.decision_logged", {
            "decision_type": "faq_response", "actor_id": str(request.user.id),
            "payload": {"conversation_id": str(conversation.id), "source": result.source},
            "ai_confidence": result.confidence,
            "ai_explainability": {"adapter": "mvp_faq_overlap", "human_review_required": result.source == "human_escalation"},
        })
        return Response({"chat_id": conversation.id, "response": result.text, "confidence": result.confidence, "source": result.source, "timestamp": response_time})


class FAQView(APIView):
    def get_permissions(self):
        if self.request.method in {"POST", "PATCH"}:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def get(self, request):
        return Response(FAQSerializer(FAQ.objects.all(), many=True).data)

    def post(self, request):
        serializer = FAQSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    def patch(self, request):
        faq_id = request.data.get("id")
        if not faq_id:
            return Response({"error": "Falta el id"}, status=400)
        faq = FAQ.objects.filter(id=faq_id).first()
        if not faq:
            return Response({"error": "FAQ no encontrada"}, status=404)
        serializer = FAQSerializer(faq, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SolicitudView(PatientOnlyMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not self.ensure_patient(request):
            return Response({"error": "Acceso exclusivo para pacientes"}, status=403)
        serializer = SolicitudSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        solicitud = serializer.save(patient_id=request.user.id, estado="pendiente")
        publicar_evento("solicitud.creada", {"solicitud_id": str(solicitud.id), "patient_id": str(solicitud.patient_id), "sintomas": solicitud.sintomas, "fuente": solicitud.fuente})
        validate_with_consortium.delay(str(solicitud.id))
        return Response(SolicitudSerializer(solicitud).data, status=201)


class ConversationDeleteView(PatientOnlyMixin, APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        if not self.ensure_patient(request):
            return Response({"error": "Acceso exclusivo para pacientes"}, status=403)
        conversation = Conversation.objects.filter(id=id, patient_id=request.user.id).first()
        if not conversation:
            return Response({"error": "Conversación no encontrada"}, status=404)
        conversation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
