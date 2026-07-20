import pytest
from tasks.send_push import send_push_notification

def test_send_push_notification_solicitud():
    result = send_push_notification('auth.account_locked', {'id': 1})
    assert result['status'] == 'simulated'

def test_send_push_notification_emergency():
    result = send_push_notification('emergency.dispatched', {'id': 2})
    assert result['status'] == 'simulated'

def test_send_push_notification_atencion():
    result = send_push_notification('teleconsult.session_started', {'id': 3})
    assert result['status'] == 'simulated'

def test_send_push_notification_unknown():
    result = send_push_notification('evento.desconocido', {'id': 4})
    assert result['status'] == 'ignored'
