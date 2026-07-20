from celery import shared_task
from apps.audit.models import DecisionIA

@shared_task
def procesar_riesgo_evaluado(event_data):
    """
    Registra de forma inmutable la decisión de IA cada vez que se evalúa un riesgo.
    (RF-18, RNF-38)
    """
    solicitud_id = event_data.get('solicitud_id')
    evaluacion_id = event_data.get('evaluacion_id')
    decision = event_data.get('decision', {})
    
    if not solicitud_id:
        return
        
    DecisionIA.objects.create(
        solicitud_id=solicitud_id,
        evaluacion_id=evaluacion_id,
        decision=decision,
        context=event_data.get('context', {})
    )
