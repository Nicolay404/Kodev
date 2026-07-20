"""Reglas MVP configurables; no son umbrales clínicos de producción."""
import json
import logging
from django.conf import settings
from django.core.cache import cache
from redis import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


def register_device(payload):
    cache.set(f"registered_device:{payload['device_id']}", str(payload["patient_id"]), timeout=None)


def is_device_registered(device_id, patient_id):
    return cache.get(f"registered_device:{device_id}") == str(patient_id)


def detect_anomalies(value: dict) -> list[str]:
    measurements = value.get("measurements", {})
    thresholds = settings.MVP_VITAL_THRESHOLDS
    anomalies = []
    for name, limits in thresholds.items():
        measured = measurements.get(name)
        if measured is None:
            continue
        if "min" in limits and measured < limits["min"]:
            anomalies.append(f"{name}:below_min")
        if "max" in limits and measured > limits["max"]:
            anomalies.append(f"{name}:above_max")
    return anomalies


def cache_reading(reading):
    try:
        client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        key = f"vitals:{reading.patient_id}"
        client.lpush(key, json.dumps({"id": str(reading.id), "device_id": str(reading.device_id), "value": reading.value, "recorded_at": reading.recorded_at.isoformat()}))
        client.ltrim(key, 0, 49)
        client.expire(key, 120)
    except RedisError:
        logger.exception("No fue posible actualizar el cache de signos vitales")
