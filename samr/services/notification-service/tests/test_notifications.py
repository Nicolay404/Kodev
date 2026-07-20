import pytest
from tasks.send_push import send_push_notification

def test_send_push_notification_solicitud():
    result = send_push_notification('solicitud.validada', {'id': 1})
    assert result == True

def test_send_push_notification_emergency():
    result = send_push_notification('emergency.dispatched', {'id': 2})
    assert result == True

def test_send_push_notification_atencion():
    result = send_push_notification('atencion.iniciada', {'id': 3})
    assert result == True

def test_send_push_notification_unknown():
    result = send_push_notification('evento.desconocido', {'id': 4})
    assert result == True
