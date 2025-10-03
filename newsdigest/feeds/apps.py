from django.apps import AppConfig


class FeedsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "feeds"

    def ready(self):
        # Import tasks for Celery autodiscovery
        from . import tasks  # noqa: F401, PLC0415
