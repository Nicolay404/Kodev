from .models import FAQ

def generate_response(message: str, context: dict) -> str:
    """
    Integración con LLM simulado.
    Por ahora, responde con una FAQ relevante si la encuentra,
    o con un mensaje genérico.
    """
    message_lower = message.lower()
    
    # Búsqueda simple en FAQs activas
    faqs = FAQ.objects.filter(is_active=True)
    for faq in faqs:
        if any(word in message_lower for word in faq.question.lower().split() if len(word) > 4):
            return f"He encontrado esta información relevante: {faq.answer}"
            
    return "Entiendo. Por favor, proporciona más detalles sobre tus síntomas para que pueda crear tu solicitud médica o ingresa la solicitud directamente."
