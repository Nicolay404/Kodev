from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_push_notification(event_type, payload):
    """
    Tarea reactiva genérica para despachar notificaciones push vía FCM (simulado).
    """
    logger.info(f"[NOTIFICACIÓN PUSH - {event_type}] payload={payload}")
    
    if event_type == 'solicitud.validada':
        logger.info(f"-> AVISO A PACIENTE: Solicitud validada, en proceso de evaluación.")
    elif event_type == 'emergency.dispatched':
        logger.info(f"-> AVISO A PACIENTE: ¡Ambulancia en camino! Mantenga la calma.")
    elif event_type == 'atencion.iniciada':
        logger.info(f"-> AVISO A PACIENTE/MÉDICO: La sesión de teleconsulta ha comenzado.")
    else:
        logger.info(f"-> Evento no mapeado para push especial, ignorando o enviando genérico.")
        
    return True
