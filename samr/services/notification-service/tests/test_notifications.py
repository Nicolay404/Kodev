import pytest
from tasks.send_push import send_push_notification


class FakeInbox:
    def store(self, event_type, payload):
        recipients = [str(payload[key]) for key in ("usuario_id", "patient_id", "professional_id") if payload.get(key)]
        return {"event_type": event_type}, recipients


@pytest.fixture(autouse=True)
def fake_inbox(monkeypatch):
    monkeypatch.setattr("tasks.send_push.get_inbox", lambda: FakeInbox())

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
