from django.contrib import admin

from .models import Article
from .models import Digest
from .models import DigestArticle
from .models import NewsSource


@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "rss_url", "active")
    list_filter = ("active",)
    search_fields = ("name", "rss_url")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "source", "published", "link")
    list_filter = ("source", "published")
    search_fields = ("title", "link", "summary")
    date_hierarchy = "published"


class DigestArticleInline(admin.TabularInline):
    model = DigestArticle
    extra = 0
    autocomplete_fields = ("article",)


@admin.register(Digest)
class DigestAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    date_hierarchy = "created_at"
    search_fields = ("name",)
    inlines = [DigestArticleInline]


@admin.register(DigestArticle)
class DigestArticleAdmin(admin.ModelAdmin):
    list_display = ("digest", "article")
    list_filter = ("digest",)
    autocomplete_fields = ("digest", "article")

# Register your models here.
