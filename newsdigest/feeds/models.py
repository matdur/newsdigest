from django.db import models


class NewsSource(models.Model):
    name = models.CharField(max_length=255)
    rss_url = models.URLField(unique=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class Article(models.Model):
    source = models.ForeignKey(
        NewsSource,
        on_delete=models.CASCADE,
        related_name="articles",
    )
    title = models.CharField(max_length=500)
    link = models.URLField(unique=True)
    published = models.DateTimeField()
    summary = models.TextField(blank=True)

    class Meta:
        ordering = ["-published"]

    def __str__(self) -> str:
        return self.title


class Digest(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.created_at:%Y-%m-%d})"


class DigestArticle(models.Model):
    digest = models.ForeignKey(
        Digest,
        on_delete=models.CASCADE,
        related_name="digest_articles",
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="in_digests",
    )

    class Meta:
        unique_together = ("digest", "article")

    def __str__(self) -> str:
        return f"{self.digest}: {self.article}"
