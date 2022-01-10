from django.apps import AppConfig


class PickPoolConfig(AppConfig):
    name = "pick_pool"

    def ready(self):
        from pick_pool import apscheduler

        apscheduler.start()
