from pytz import utc

from apscheduler.schedulers.background import BackgroundScheduler

from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from nfl.api import EspnApiClient


def nfl_check_games():
    api_client = EspnApiClient()
    api_client.check_games()


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


def start():
    scheduler = BackgroundScheduler(timezone=utc)
    scheduler.add_jobstore(DjangoJobStore(), "default")
    scheduler.start()
    scheduler.add_job(
        nfl_check_games,
        "cron",
        minute="*/5",
        id="nfl_check_games",
        max_instances=1,
        replace_existing=True,
    )
    scheduler.add_job(
        delete_old_job_executions,
        "cron",
        day_of_week="mon",
        hour="00",
        minute="00",
        id="delete_old_job_executions",
        max_instances=1,
        replace_existing=True,
    )
