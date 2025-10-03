from django.db import migrations


def create_periodic_task(apps, schema_editor):
    IntervalSchedule = apps.get_model("django_celery_beat", "IntervalSchedule")
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")

    # Ensure an interval schedule exists for every 15 minutes
    interval, _ = IntervalSchedule.objects.get_or_create(every=15, period="minutes")

    # Create or update the periodic task for fetching RSS feeds
    task_name = "Fetch RSS feeds"
    task_path = "feeds.tasks.fetch_feeds"

    task, created = PeriodicTask.objects.get_or_create(
        name=task_name,
        defaults={
            "interval": interval,
            "task": task_path,
            "enabled": True,
        },
    )

    if not created:
        # Update existing task to ensure correct interval and task path
        task.interval = interval
        task.task = task_path
        task.enabled = True
        task.save(update_fields=["interval", "task", "enabled"])


def remove_periodic_task(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    PeriodicTask.objects.filter(name="Fetch RSS feeds").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("feeds", "0001_initial"),
        ("django_celery_beat", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_periodic_task, remove_periodic_task),
    ]


