from django.urls import path
from .views import ChatView, ConversationDeleteView, FAQView, SolicitudDetailView, SolicitudView

urlpatterns = [
    path('chat/', ChatView.as_view(), name='chat'),
    path('faq/', FAQView.as_view(), name='faq'),
    path('', SolicitudView.as_view(), name='solicitud_create'),
    path('<uuid:id>/', SolicitudDetailView.as_view(), name='solicitud_detail'),
    path('conversations/<uuid:id>/', ConversationDeleteView.as_view(), name='conversation_delete'),
]
