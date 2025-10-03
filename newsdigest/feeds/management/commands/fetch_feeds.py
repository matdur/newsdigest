from django.core.management.base import BaseCommand

from feeds.tasks import fetch_feeds


class Command(BaseCommand):
    help = "Fetch RSS feeds from active news sources and store new articles."

    def handle(self, *args, **options):
        # Run task synchronously via Celery app
        result = fetch_feeds.apply(args=()).get()
        created_total = (
            result.get("created_total") if isinstance(result, dict) else result
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Fetched feeds. New articles: {created_total}",
            ),
        )
