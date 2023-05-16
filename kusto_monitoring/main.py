import logging
import signal

from .scheduler import Task, Scheduler
from .config import get_conf
from .kusto import run_query, check_connectivity
from .email import send_alert
from pathlib import Path


def setup_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(module)s: %(message)s"
    )
    logging.getLogger("azure").setLevel(logging.WARNING)


def run_task(alert_name, kql):
    r = run_query(kql, retries=3)
    if not r.is_empty():
        send_alert(alert_name, r.to_html())


def schedule_tasks() -> Scheduler:
    tasks = []
    logging.info("Scanning queries/ folder for new tasks")
    for f in (Path(__file__).parent.parent / "queries").glob("*.kql"):
        kql = f.read_text()
        alert_name = f.name.replace(".kql", "").replace("_", " ")
        schedule = kql.split("\n")[0].lstrip("/").strip()
        tasks.append(Task(alert_name, schedule, run_task, alert_name, kql))
        logging.info(f"Scheduled alert '{alert_name}' for '{schedule}'")
    return Scheduler(tasks)


_scheduler = None


def stop_scheduler(*args):
    if _scheduler is not None:
        logging.info("Re-scanning new tasks in a minute")
        _scheduler.stop()


if __name__ == "__main__":
    setup_logging()
    check_connectivity()

    signal.signal(signal.SIGHUP, stop_scheduler)
    while True:
        _scheduler = schedule_tasks()
        _scheduler.run()
