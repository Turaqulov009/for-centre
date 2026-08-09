from django.db import models


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=120, default="FOR CENTRE")
    hero_title = models.CharField(max_length=200, blank=True)
    hero_text = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    telegram = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    work_time = models.CharField(max_length=120, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sayt sozlamasi"
        verbose_name_plural = "Sayt sozlamalari"

    def __str__(self):
        return self.site_name or "Sayt sozlamalari"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Banner(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to="banners/", blank=True, null=True)
    button_text = models.CharField(max_length=80, blank=True)
    button_url = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "-created_at"]
        verbose_name = "Banner"
        verbose_name_plural = "Bannerlar"

    def __str__(self):
        return self.title


class Feature(models.Model):
    """Landing: afzalliklar."""

    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=80,
        blank=True,
        help_text="Masalan: fa-solid fa-rocket",
    )
    is_active = models.BooleanField(default=True, db_index=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "title"]
        verbose_name = "Afzallik"
        verbose_name_plural = "Afzalliklar"

    def __str__(self):
        return self.title


class News(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    excerpt = models.CharField(max_length=300, blank=True)
    body = models.TextField(blank=True)
    cover = models.ImageField(upload_to="news/", blank=True, null=True)
    is_published = models.BooleanField(default=False, db_index=True)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "Yangilik"
        verbose_name_plural = "Yangiliklar"

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    is_active = models.BooleanField(default=True, db_index=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"

    def __str__(self):
        return self.question


class Lead(models.Model):
    """Saytdan kelgan ariza."""

    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    course_interest = models.CharField(max_length=150, blank=True)
    message = models.TextField(blank=True)
    is_contacted = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Ariza"
        verbose_name_plural = "Arizalar"

    def __str__(self):
        return f"{self.name} — {self.phone}"
