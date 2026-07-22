import json
import uuid
from datetime import datetime, timezone

import redis
from django.conf import settings


def recipient_ids(payload):
    return sorted(
        {
            str(payload[key])
            for key in ("usuario_id", "patient_id", "professional_id")
            if payload.get(key)
        }
    )


class NotificationInbox:
    def __init__(self, client=None):
        self.client = client or redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

    @staticmethod
    def _key(recipient_id):
        return f"notifications:{recipient_id}"

    def store(self, event_type, payload):
        notification = {
            "id": str(uuid.uuid4()),
            "event_type": event_type,
            "payload": payload,
            "read": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        encoded = json.dumps(notification, ensure_ascii=False, separators=(",", ":"))
        recipients = recipient_ids(payload)
        for recipient_id in recipients:
            key = self._key(recipient_id)
            with self.client.pipeline() as pipe:
                pipe.lpush(key, encoded)
                pipe.ltrim(key, 0, settings.NOTIFICATION_INBOX_LIMIT - 1)
                pipe.expire(key, settings.NOTIFICATION_TTL_SECONDS)
                pipe.execute()
        return notification, recipients

    def list_for(self, recipient_id):
        return [json.loads(item) for item in self.client.lrange(self._key(recipient_id), 0, -1)]

    def mark_read(self, recipient_id, notification_id):
        key = self._key(recipient_id)
        notifications = self.list_for(recipient_id)
        found = None
        for notification in notifications:
            if notification["id"] == str(notification_id):
                notification["read"] = True
                found = notification
                break
        if not found:
            return None
        encoded = [json.dumps(item, ensure_ascii=False, separators=(",", ":")) for item in notifications]
        with self.client.pipeline() as pipe:
            pipe.delete(key)
            if encoded:
                pipe.rpush(key, *encoded)
                pipe.expire(key, settings.NOTIFICATION_TTL_SECONDS)
            pipe.execute()
        return found


def get_inbox():
    return NotificationInbox()
