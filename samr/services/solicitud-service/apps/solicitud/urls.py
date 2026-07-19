from django.urls import path
from .views import ChatView, FAQView, SolicitudView, ConversationDeleteView

urlpatterns = [
    path('chat/', ChatView.as_view(), name='chat'),
    path('faq/', FAQView.as_view(), name='faq'),
    path('', SolicitudView.as_view(), name='solicitud_create'),
    path('conversations/<int:id>/', ConversationDeleteView.as_view(), name='conversation_delete'),
]
