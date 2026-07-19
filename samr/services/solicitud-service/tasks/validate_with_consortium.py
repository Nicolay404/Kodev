from celery import shared_task
import requests
from apps.solicitud.models import Solicitud, ConsorcioValidationLog
from events.publisher import publicar_evento

@shared_task
def validate_with_consortium(solicitud_id):
    try:
        solicitud = Solicitud.objects.get(id=solicitud_id)
    except Solicitud.DoesNotExist:
        return

    payload = {
        'patient_id': solicitud.patient_id,
        'description': solicitud.description,
        'symptoms': solicitud.symptoms,
        'urgency': solicitud.urgency,
    }

    try:
        # Llama API del Consorcio con timeout de 5s (RNF-07)
        response = requests.post('http://consorcio/validate', json=payload, timeout=5.0)
        
        if response.status_code == 200:
            solicitud.estado = 'validada'
            solicitud.consorcio_validation_id = response.json().get('validation_id', 'unknown')
            solicitud.save()
            
            ConsorcioValidationLog.objects.create(solicitud=solicitud, status='OK', response=response.json())
            
            publicar_evento('solicitud.validada', {
                'solicitud_id': solicitud.id,
                'patient_id': solicitud.patient_id,
                'urgency': solicitud.urgency
            })
        else:
            solicitud.estado = 'rechazada'
            solicitud.save()
            
            ConsorcioValidationLog.objects.create(solicitud=solicitud, status='REJECTED', response={'status_code': response.status_code})
            
            publicar_evento('solicitud.rechazada', {
                'solicitud_id': solicitud.id,
                'patient_id': solicitud.patient_id,
                'reason': 'Consortium rejected'
            })
            
    except requests.exceptions.Timeout:
        solicitud.estado = 'pendiente_reintento'
        solicitud.save()
        ConsorcioValidationLog.objects.create(solicitud=solicitud, status='TIMEOUT', response=None)
        
    except requests.exceptions.RequestException as e:
        solicitud.estado = 'pendiente_reintento'
        solicitud.save()
        ConsorcioValidationLog.objects.create(solicitud=solicitud, status='ERROR', response={'error': str(e)})
