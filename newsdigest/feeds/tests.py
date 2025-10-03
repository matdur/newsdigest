from __future__ import annotations

from datetime import UTC
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from .models import Article
from .models import Digest
from .models import DigestArticle
from .models import NewsSource
from .tasks import fetch_feeds


class ModelsTestCase(TestCase):
    def test_create_models_and_str(self):
        source = NewsSource.objects.create(
            name="Example",
            rss_url="https://example.com/rss",
            active=True,
        )
        article = Article.objects.create(
            source=source,
            title="Title",
            link="https://example.com/a1",
            published=timezone.now(),
            summary="",
        )
        digest = Digest.objects.create(name="Weekly")
        da = DigestArticle.objects.create(digest=digest, article=article)

        assert str(source) == "Example"
        assert str(article) == "Title"
        assert "Weekly" in str(digest)
        assert "Weekly" in str(da)

    def test_digest_article_unique_constraint(self):
        source = NewsSource.objects.create(
            name="S",
            rss_url="https://s.com/rss",
            active=True,
        )
        article = Article.objects.create(
            source=source,
            title="T",
            link="https://s.com/a",
            published=timezone.now(),
            summary="",
        )
        digest = Digest.objects.create(name="D")
        DigestArticle.objects.create(digest=digest, article=article)
        with pytest.raises(IntegrityError):
            # Any IntegrityError subclass is fine; DB backend may vary
            DigestArticle.objects.create(digest=digest, article=article)


class FetchFeedsTaskTestCase(TestCase):
    def setUp(self):
        self.active_source = NewsSource.objects.create(
            name="Active", rss_url="https://active.test/rss", active=True,
        )
        self.inactive_source = NewsSource.objects.create(
            name="Inactive", rss_url="https://inactive.test/rss", active=False,
        )

    def _fake_parsed(self, entries):
        # feedparser.parse returns an object with .entries list
        return SimpleNamespace(entries=entries)

    @patch("feeds.tasks.feedparser.parse")
    def test_only_active_sources_processed(self, mock_parse):
        mock_parse.side_effect = lambda url: self._fake_parsed(
            [
                {
                    "link": f"{url}/a1",
                    "title": "Article 1",
                    "published_parsed": datetime.now(tz=UTC).timetuple(),
                },
            ],
        )
        result = fetch_feeds.apply(args=()).get()

        assert Article.objects.count() == 1
        assert Article.objects.first().source == self.active_source
        assert result["created_total"] == 1
        assert len(result["sources"]) == 1
        assert result["sources"][0]["source"] == "Active"

    @patch("feeds.tasks.feedparser.parse")
    def test_deduplicates_by_link(self, mock_parse):
        entries = [
            {"link": "https://active.test/rss/a1", "title": "A1"},
            {"link": "https://active.test/rss/a1", "title": "A1 duplicate"},
        ]
        mock_parse.return_value = self._fake_parsed(entries)

        first = fetch_feeds.apply(args=()).get()
        second = fetch_feeds.apply(args=()).get()

        assert Article.objects.count() == 1
        assert first["created_total"] == 1
        assert second["created_total"] == 0

    @patch("feeds.tasks.feedparser.parse")
    def test_published_and_summary_fallbacks(self, mock_parse):
        mock_parse.return_value = self._fake_parsed(
            [
                {
                    "link": "https://active.test/rss/a2",
                    # Title falls back to link and published falls back to now
                    "description": "desc only",
                },
            ],
        )
        before = timezone.now()
        fetch_feeds.apply(args=()).get()
        after = timezone.now()

        art = Article.objects.get(link="https://active.test/rss/a2")
        assert art.title == art.link
        assert before <= art.published <= after
        assert art.summary == "desc only"

