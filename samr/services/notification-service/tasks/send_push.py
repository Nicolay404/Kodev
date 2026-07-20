"""Despacho de notificaciones mediante un adaptador simulado reemplazable."""

import logging
import os

from celery import shared_task

logger = logging.getLogger(__name__)

SUPPORTED_EVENTS = {
    "auth.account_locked",
    "vitals.critical_detected",
    "vity.escalation_requested",
    "recursos.asignados",
    "center.validated",
    "center.rejected",
    "emergency.created",
    "emergency.dispatched",
    "teleconsult.session_started",
}


class MVPLogNotificationAdapter:
    def send(self, event_type, payload):
        logger.info("MVP_NOTIFICATION event=%s payload=%s", event_type, payload)
        return {"status": "simulated", "event_type": event_type}


@shared_task
def send_push_notification(event_type, payload):
    if event_type not in SUPPORTED_EVENTS:
        return {"status": "ignored", "event_type": event_type}
    if os.environ.get("MVP_NOTIFICATION_BACKEND", "log") != "log":
        raise RuntimeError("Backend de notificacion no configurado")
    return MVPLogNotificationAdapter().send(event_type, payload)
