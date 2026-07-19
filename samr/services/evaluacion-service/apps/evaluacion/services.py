def evaluate_risk(solicitud_data: dict) -> dict:
    """
    Simulación de evaluación de riesgo usando IA / RAG.
    Devuelve un score y recomendaciones.
    """
    # En producción esto llamaría a un modelo ML o RAG
    urgency = solicitud_data.get('urgency', 'low')
    score = 0.5
    if urgency == 'high':
        score = 0.9
    elif urgency == 'medium':
        score = 0.7
        
    recomendaciones = {
        'protocolo': 'Estándar',
        'requiere_ambulancia': score > 0.8
    }
    
    return {
        'score': score,
        'recomendaciones': recomendaciones
    }

def find_best_center(evaluacion_id: int) -> dict:
    """
    Encuentra el mejor centro disponible basado en la evaluación.
    """
    # Lógica simplificada
    return {
        'centro_asignado': 'Hospital General',
        'recursos': ['cama', 'oxigeno']
    }
