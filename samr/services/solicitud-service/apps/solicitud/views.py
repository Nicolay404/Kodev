from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, FAQ, Solicitud
from .serializers import ChatMessageSerializer, FAQSerializer, SolicitudSerializer
from .services import generate_response
from .permissions import IsAdminUser
from events.publisher import publicar_evento
from tasks.validate_with_consortium import validate_with_consortium
import datetime

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        message = serializer.validated_data['message']
        chat_id = serializer.validated_data.get('chat_id')
        
        if chat_id:
            try:
                conversation = Conversation.objects.get(id=chat_id, patient_id=request.user.id)
            except Conversation.DoesNotExist:
                return Response({'error': 'Conversación no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        else:
            conversation = Conversation.objects.create(patient_id=request.user.id)
            
        # Almacenar mensaje del paciente
        timestamp = datetime.datetime.now().isoformat()
        conversation.messages.append({'role': 'user', 'content': message, 'timestamp': timestamp})
        
        # Generar respuesta
        context = {'history': conversation.messages}
        response_text = generate_response(message, context)
        
        # Almacenar respuesta
        resp_timestamp = datetime.datetime.now().isoformat()
        conversation.messages.append({'role': 'assistant', 'content': response_text, 'timestamp': resp_timestamp})
        conversation.save()
        
        return Response({
            'chat_id': conversation.id,
            'response': response_text,
            'timestamp': resp_timestamp
        })

class FAQView(APIView):
    def get_permissions(self):
        if self.request.method in ['POST', 'PATCH']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def get(self, request):
        faqs = FAQ.objects.all()
        serializer = FAQSerializer(faqs, many=True)
        return Response(serializer.data)
        
    def post(self, request):
        serializer = FAQSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def patch(self, request):
        faq_id = request.data.get('id')
        if not faq_id:
            return Response({'error': 'Falta el id'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            faq = FAQ.objects.get(id=faq_id)
        except FAQ.DoesNotExist:
            return Response({'error': 'FAQ no encontrada'}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = FAQSerializer(faq, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SolicitudView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SolicitudSerializer(data=request.data)
        if serializer.is_valid():
            solicitud = serializer.save(patient_id=request.user.id, estado='pendiente')
            
            # Publicar evento
            publicar_evento('solicitud.creada', {
                'solicitud_id': solicitud.id,
                'patient_id': solicitud.patient_id,
                'urgency': solicitud.urgency
            })
            
            # Ejecutar tarea asíncrona de Celery
            validate_with_consortium.delay(solicitud.id)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ConversationDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        try:
            conversation = Conversation.objects.get(id=id, patient_id=request.user.id)
            conversation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Conversation.DoesNotExist:
            return Response({'error': 'Conversación no encontrada'}, status=status.HTTP_404_NOT_FOUND)
