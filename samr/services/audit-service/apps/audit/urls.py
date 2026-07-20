from django.urls import path
from .views import AuditDecisionsView, AuditDecisionReviewView

urlpatterns = [
    path('decisions/', AuditDecisionsView.as_view(), name='audit_decisions'),
    path('decisions/<int:audit_log_id>/review/', AuditDecisionReviewView.as_view(), name='audit_review'),
]
