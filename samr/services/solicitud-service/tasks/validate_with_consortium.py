import logging
from celery import shared_task
from apps.solicitud.models import Solicitud
from apps.solicitud.services import get_consortium_adapter
from events.publisher import publicar_evento

logger = logging.getLogger(__name__)


@shared_task
def validate_with_consortium(solicitud_id):
    try:
        solicitud = Solicitud.objects.get(id=solicitud_id)
    except Solicitud.DoesNotExist:
        return "not_found"
    try:
        result = get_consortium_adapter().validate(solicitud)
    except (TimeoutError, ConnectionError) as exc:
        solicitud.estado = "pendiente_reintento"
        solicitud.save(update_fields=["estado"])
        logger.warning("Validación M2M pendiente de reintento: %s", exc)
        return "pending_retry"
    solicitud.estado = "validada" if result.accepted else "rechazada"
    solicitud.save(update_fields=["estado"])
    if result.accepted:
        publicar_evento("solicitud.validada", {"solicitud_id": str(solicitud.id), "patient_id": str(solicitud.patient_id), "sintomas": solicitud.sintomas, "datos_biomedicos": solicitud.datos_biomedicos})
    return solicitud.estado
