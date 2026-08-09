from django.contrib import admin

from .models import FAQ, Banner, Feature, Lead, News, SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "phone", "email", "updated_at")


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "sort_order", "created_at")
    list_filter = ("is_active",)
    list_editable = ("is_active", "sort_order")


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "published_at")
    list_filter = ("is_published",)
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "excerpt", "body")


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "course_interest", "is_contacted", "created_at")
    list_filter = ("is_contacted",)
    search_fields = ("name", "phone", "email", "message")
