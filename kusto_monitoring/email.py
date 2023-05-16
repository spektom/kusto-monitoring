import logging

from .config import get_conf
from azure.communication.email import EmailClient


def send_alert(alert_name, result):
    email_client = EmailClient.from_connection_string(
        get_conf("AZURE_COMMUNICATION_CONNECTION_STRING"), enable_logging=False
    )
    message = {
        "content": {
            "subject": f"Kusto monitoring alert: {alert_name}",
            "html": f"<html>{result}</html>",
        },
        "recipients": {"to": [{"address": r} for r in get_conf("RECIPIENTS").split()]},
        "senderAddress": get_conf("AZURE_COMMUNICATION_SENDER"),
    }
    email_client.begin_send(message)
