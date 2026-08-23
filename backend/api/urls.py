from django.urls import path
from api.views import (
    OverviewAPIView,
    LivenessHealthAPIView,
    ReadinessHealthAPIView,
    DomainDetailAPIView,
    DataQualityAPIView,
    MLPredictAPIView,
    CopilotAPIView,
    SupersetStatusAPIView,
    CreditCardTelemetryAPIView,
    CreditCardSimulateAPIView,
    CreditCardTransactionDetailAPIView,
    CreditCardSSEEventStreamAPIView
)

urlpatterns = [
    path('v1/health/liveness/', LivenessHealthAPIView.as_view(), name='health-liveness'),
    path('v1/health/readiness/', ReadinessHealthAPIView.as_view(), name='health-readiness'),
    path('v1/overview/', OverviewAPIView.as_view(), name='overview'),
    path('v1/domains/<str:domain_name>/', DomainDetailAPIView.as_view(), name='domain-detail'),
    path('v1/quality/telemetry/', DataQualityAPIView.as_view(), name='quality-telemetry'),
    path('v1/ml/predict/', MLPredictAPIView.as_view(), name='ml-predict'),
    path('v1/copilot/query/', CopilotAPIView.as_view(), name='copilot-query'),
    path('v1/superset/status/', SupersetStatusAPIView.as_view(), name='superset-status'),
    
    # Real-Time Credit Card Fraud Streaming Endpoints
    path('v1/stream/credit-cards/telemetry/', CreditCardTelemetryAPIView.as_view(), name='stream-telemetry'),
    path('v1/stream/credit-cards/simulate/', CreditCardSimulateAPIView.as_view(), name='stream-simulate'),
    path('v1/stream/credit-cards/events/', CreditCardSSEEventStreamAPIView.as_view(), name='stream-events'),
    path('v1/stream/credit-cards/transaction/<str:event_id>/', CreditCardTransactionDetailAPIView.as_view(), name='stream-txn-detail'),
]
