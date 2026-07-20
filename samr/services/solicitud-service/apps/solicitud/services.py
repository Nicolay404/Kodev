"""Puertos y adaptadores MVP reemplazables para FAQ/LLM y Consorcio."""
import hashlib
from dataclasses import dataclass
from django.conf import settings
from django.core.cache import cache
from .models import FAQ


@dataclass(frozen=True)
class ChatResult:
    text: str
    confidence: float
    source: str


@dataclass(frozen=True)
class ConsortiumResult:
    accepted: bool
    reason: str


class MVPChatAdapter:
    """Simulador no clínico: solo recupera respuestas FAQ administradas."""
    fallback = "No tengo una respuesta verificada para esa consulta. Un profesional debe revisarla; si presenta una emergencia, contacte a los servicios de emergencia."

    @staticmethod
    def _tokens(text):
        return {word.strip(".,;:¿?¡!").lower() for word in text.split() if len(word) >= 3}

    def respond(self, message: str) -> ChatResult:
        cache_key = f"vity_cache:{hashlib.sha256(message.strip().lower().encode()).hexdigest()}"
        cached = cache.get(cache_key)
        if cached:
            return ChatResult(**cached)
        query = self._tokens(message)
        best = None
        best_score = 0.0
        for faq in FAQ.objects.all():
            target = self._tokens(faq.question)
            score = len(query & target) / max(len(query | target), 1)
            if score > best_score:
                best, best_score = faq, score
        if best and best_score >= settings.MVP_FAQ_CONFIDENCE_THRESHOLD:
            result = ChatResult(best.answer, round(best_score, 3), "faq")
        else:
            result = ChatResult(self.fallback, round(best_score, 3), "human_escalation")
        cache.set(cache_key, result.__dict__, timeout=60)
        return result


class MVPConsortiumAdapter:
    """Simula validación estructural; no representa una API real del Consorcio."""
    def validate(self, solicitud) -> ConsortiumResult:
        outcome = settings.MVP_CONSORTIUM_OUTCOME
        if outcome == "timeout":
            raise TimeoutError("Timeout simulado del Consorcio")
        if outcome == "rejected":
            return ConsortiumResult(False, "Rechazo configurado en simulador MVP")
        accepted = bool(solicitud.patient_id and solicitud.sintomas)
        return ConsortiumResult(accepted, "Estructura válida" if accepted else "Faltan datos obligatorios")


def get_chat_adapter():
    return MVPChatAdapter()


def get_consortium_adapter():
    return MVPConsortiumAdapter()
