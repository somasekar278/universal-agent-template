"""Alerting System"""
from enum import Enum
from dataclasses import dataclass

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class Alert:
    message: str
    severity: AlertSeverity

class AlertManager:
    """Alert manager for production monitoring"""
    def send_alert(self, alert: Alert):
        print(f"🚨 [{alert.severity.value.upper()}] {alert.message}")
