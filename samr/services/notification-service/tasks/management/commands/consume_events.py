from django.core.management.base import BaseCommand
from events.consumer import iniciar_consumidor
from tasks.send_push import SUPPORTED_EVENTS, send_push_notification


class Command(BaseCommand):
    def handle(self, *args, **options):
        iniciar_consumidor("notification-service.queue", sorted(SUPPORTED_EVENTS), lambda event_type, payload: send_push_notification.delay(event_type, payload))
