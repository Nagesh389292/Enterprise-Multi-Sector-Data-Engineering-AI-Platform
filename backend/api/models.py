"""
Django Models for Enterprise Platform Data Layer.
Stores processed Credit Card transactions and Fraud Alerts in Database (PostgreSQL / SQLite).
"""

from django.db import models

class CreditCardTransaction(models.Model):
    event_id = models.CharField(max_length=64, unique=True, primary_key=True)
    customer_id = models.CharField(max_length=64)
    amount = models.FloatField()
    merchant = models.CharField(max_length=128)
    location = models.CharField(max_length=128)
    device_id = models.CharField(max_length=64)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=32, default="PROCESSED")
    fraud_probability = models.FloatField(default=0.0)
    risk_score = models.IntegerField(default=0)
    risk_level = models.CharField(max_length=16, default="LOW")
    is_fraud_predicted = models.IntegerField(default=0)
    explanation_reasons = models.JSONField(default=list)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.event_id} - ${self.amount} ({self.risk_level})"


class FraudAlert(models.Model):
    alert_id = models.AutoField(primary_key=True)
    transaction = models.ForeignKey(CreditCardTransaction, on_delete=models.CASCADE, related_name="alerts")
    triggered_at = models.DateTimeField(auto_now_add=True)
    risk_score = models.IntegerField()
    reasons = models.JSONField()

    class Meta:
        ordering = ['-triggered_at']

    def __str__(self):
        return f"Alert {self.alert_id} for Txn {self.transaction.event_id} (Score: {self.risk_score})"
