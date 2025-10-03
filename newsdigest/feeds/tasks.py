from __future__ import annotations

from datetime import UTC
from datetime import datetime

import feedparser
from celery import shared_task
from django.utils import timezone

from .models import Article
from .models import NewsSource


@shared_task(bind=True, ignore_result=False)
def fetch_feeds(self) -> dict:
    created_total = 0
    sources_checked: list[dict] = []

    for source in NewsSource.objects.filter(active=True):
        created_count = 0
        parsed = feedparser.parse(source.rss_url)
        entries: list[dict] = getattr(parsed, "entries", []) or []
        for entry in entries:
            link = entry.get("link")
            if not link:
                continue

            published_dt = _coerce_published(entry)
            title = entry.get("title") or link
            summary = entry.get("summary") or entry.get("description") or ""

            _article, created = Article.objects.get_or_create(
                link=link,
                defaults={
                    "source": source,
                    "title": title[:500],
                    "published": published_dt or timezone.now(),
                    "summary": summary or "",
                },
            )
            if created:
                created_count += 1
        sources_checked.append({"source": source.name, "new_articles": created_count})
        created_total += created_count

    return {"created_total": created_total, "sources": sources_checked}


def _coerce_published(entry: dict) -> datetime | None:
    # Try multiple common fields from feedparser
    for key in ("published_parsed", "updated_parsed"):
        struct = entry.get(key)
        if struct:
            try:
                # feedparser returns time.struct_time
                return datetime(*struct[:6], tzinfo=UTC)
            except Exception:  # noqa: S112, BLE001
                # If conversion fails, try the next key
                continue
    return None

