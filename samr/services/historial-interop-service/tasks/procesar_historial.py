from celery import shared_task
from apps.historial.models import Historial

@shared_task
def procesar_caso_cerrado(event_data):
    """
    Consolida el historial clínico cuando se recibe el evento de 'caso.cerrado'.
    """
    patient_id = event_data.get('patient_id')
    if not patient_id:
        return
        
    historial, created = Historial.objects.get_or_create(patient_id=patient_id)
    
    # Agregar el nuevo caso al JSON array del historial
    nuevo_registro = {
        'tipo': 'caso_cerrado',
        'caso_id': event_data.get('caso_id'),
        'closed_at': event_data.get('closed_at'),
        'notes': event_data.get('notes')
    }
    
    historial.data.append(nuevo_registro)
    historial.save()
