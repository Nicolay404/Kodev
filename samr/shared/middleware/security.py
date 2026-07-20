"""Trazabilidad y validación HTTP común para servicios Django."""

import uuid

from django.http import JsonResponse


class RequestSecurityMiddleware:
    BODY_METHODS = {"POST", "PUT", "PATCH"}
    JSON_CONTENT_TYPES = {"application/json", "application/fhir+json"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.request_id = request_id
        if request.method in self.BODY_METHODS and request.body:
            content_type = request.content_type or ""
            if content_type not in self.JSON_CONTENT_TYPES:
                response = JsonResponse(
                    {"error": "Content-Type debe ser application/json"}, status=415
                )
                response["X-Request-ID"] = request_id
                return response
        response = self.get_response(request)
        response["X-Request-ID"] = request_id
        return response
