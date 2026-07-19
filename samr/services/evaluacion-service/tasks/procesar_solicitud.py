from celery import shared_task
from apps.evaluacion.models import Evaluacion
from apps.evaluacion.services import evaluate_risk
from events.publisher import publicar_evento

@shared_task
def procesar_solicitud_validada(solicitud_data):
    """
    Tarea consumida asíncronamente cuando llega el evento solicitud.validada
    """
    solicitud_id = solicitud_data.get('solicitud_id')
    if not solicitud_id:
        return
        
    if Evaluacion.objects.filter(solicitud_id=solicitud_id).exists():
        return
        
    resultado = evaluate_risk(solicitud_data)
    
    evaluacion = Evaluacion.objects.create(
        solicitud_id=solicitud_id,
        riesgo_score=resultado['score'],
        recomendaciones=resultado['recomendaciones']
    )
    
    publicar_evento('riesgo.evaluado', {
        'evaluacion_id': evaluacion.id,
        'solicitud_id': solicitud_id,
        'score': evaluacion.riesgo_score
    })
