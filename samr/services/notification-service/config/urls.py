from django.urls import path

from apps.notifications.views import health, notification_list, notification_mark_read


urlpatterns = [
    path("health", health, name="health"),
    path("api/notifications/", notification_list, name="notification_list"),
    path("api/notifications/<uuid:notification_id>/read/", notification_mark_read, name="notification_mark_read"),
]
