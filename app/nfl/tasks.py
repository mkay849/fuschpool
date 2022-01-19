from huey import crontab
from huey.contrib.djhuey import periodic_task


@periodic_task(crontab(minute="*/15"))
def nfl_check_games():
    from .api import EspnApiClient

    c = EspnApiClient()
    c.check_games()
