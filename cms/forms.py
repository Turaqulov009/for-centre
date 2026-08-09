from django import forms
from django.utils.text import slugify

from .models import FAQ, Banner, Feature, Lead, News, SiteSettings


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ["name", "phone", "email", "course_interest", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Ismingiz"}),
            "phone": forms.TextInput(attrs={"placeholder": "Telefon", "type": "tel"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
            "course_interest": forms.TextInput(attrs={"placeholder": "Kurs"}),
            "message": forms.Textarea(attrs={"rows": 3, "placeholder": "Izoh"}),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = "".join(ch for ch in phone if ch.isdigit())
        if len(digits) < 9:
            raise forms.ValidationError("Telefon raqamini to‘g‘ri kiriting.")
        return phone


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            "site_name",
            "hero_title",
            "hero_text",
            "phone",
            "email",
            "telegram",
            "address",
            "work_time",
        ]
        widgets = {
            "hero_text": forms.Textarea(attrs={"rows": 4}),
        }


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = [
            "title",
            "subtitle",
            "image",
            "button_text",
            "button_url",
            "is_active",
            "sort_order",
        ]


class FeatureForm(forms.ModelForm):
    class Meta:
        model = Feature
        fields = ["title", "description", "icon", "is_active", "sort_order"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "icon": forms.TextInput(attrs={"placeholder": "fa-solid fa-rocket"}),
        }


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = [
            "title",
            "slug",
            "excerpt",
            "body",
            "cover",
            "is_published",
            "published_at",
        ]
        widgets = {
            "excerpt": forms.TextInput(attrs={"placeholder": "Qisqa matn"}),
            "body": forms.Textarea(attrs={"rows": 8}),
            "slug": forms.TextInput(attrs={"placeholder": "Bo‘sh qoldirilsa avtomatik"}),
            "published_at": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={"type": "datetime-local"},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["published_at"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]
        self.fields["slug"].required = False

    def clean(self):
        cleaned = super().clean()
        slug = (cleaned.get("slug") or "").strip()
        title = (cleaned.get("title") or "").strip()
        if not slug:
            slug = slugify(title) or "news"
        base = slug
        n = 2
        qs = News.objects.filter(slug=slug)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        while qs.exists():
            slug = f"{base}-{n}"
            n += 1
            qs = News.objects.filter(slug=slug)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
        cleaned["slug"] = slug
        return cleaned


class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ["question", "answer", "is_active", "sort_order"]
        widgets = {
            "answer": forms.Textarea(attrs={"rows": 4}),
        }
