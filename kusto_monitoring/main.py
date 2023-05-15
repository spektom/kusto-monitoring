import logging
import kusto_monitoring.kusto as kusto

from .scheduler import Task, Scheduler
from .config import get_conf

from pathlib import Path
from azure.communication.email import EmailClient


def run_query_and_send_alert(alert_name, kql):
    r = kusto.run_query(kql, retries=3)
    if not r.is_empty():
        body = r.to_html()
        email_client = EmailClient.from_connection_string(
            get_conf("AZURE_COMMUNICATION_CONNECTION_STRING"), enable_logging=False
        )
        message = {
            "content": {
                "subject": f"Kusto monitoring alert: {alert_name}",
                "html": f"<html>{body}</html>",
            },
            "recipients": {
                "to": [{"address": r} for r in get_conf("RECIPIENTS").split()]
            },
            "senderAddress": get_conf("AZURE_COMMUNICATION_SENDER"),
        }
        email_client.begin_send(message)


def schedule_tasks() -> Scheduler:
    tasks = []
    for f in (Path(__file__).parent.parent / "queries").glob("*.kql"):
        kql = f.read_text()
        alert_name = f.name.replace(".kql", "").replace("_", " ")
        schedule = kql.split("\n")[0].lstrip("/").strip()
        tasks.append(
            Task(alert_name, schedule, run_query_and_send_alert, alert_name, kql)
        )
        logging.info(f"Scheduled alert '{alert_name}' for '{schedule}'")
    return Scheduler(tasks)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(module)s: %(message)s"
    )
    logging.getLogger("azure").setLevel(logging.WARNING)

    kusto.check_connectivity()
    schedule_tasks().run()
