from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.permissions import admin_required
from cms.forms import BannerForm, FAQForm, FeatureForm, NewsForm, SiteSettingsForm
from cms.models import FAQ, Banner, Feature, Lead, News, SiteSettings


def _admin_shell(request, template, context=None):
    ctx = context or {}
    return render(request, template, ctx)


@admin_required
@require_http_methods(["GET", "POST"])
def admin_settings(request):
    site = SiteSettings.get_solo()
    form = SiteSettingsForm(request.POST or None, instance=site)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Sayt sozlamalari saqlandi.")
        return redirect("portal:admin_settings")
    return _admin_shell(
        request,
        "portal/admin/settings.html",
        {"form": form, "site": site},
    )


# ---- Banner ----


@admin_required
def admin_banners(request):
    return _admin_shell(
        request,
        "portal/admin/banners.html",
        {"items": Banner.objects.all()},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_banner_create(request):
    form = BannerForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Banner yaratildi.")
        return redirect("portal:admin_banners")
    return _admin_shell(
        request,
        "portal/admin/banner_form.html",
        {"form": form, "title": "Yangi banner"},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_banner_edit(request, pk):
    obj = get_object_or_404(Banner, pk=pk)
    form = BannerForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Banner yangilandi.")
        return redirect("portal:admin_banners")
    return _admin_shell(
        request,
        "portal/admin/banner_form.html",
        {"form": form, "title": "Banner tahrirlash", "obj": obj},
    )


@admin_required
@require_http_methods(["POST"])
def admin_banner_delete(request, pk):
    obj = get_object_or_404(Banner, pk=pk)
    obj.delete()
    messages.success(request, "Banner o‘chirildi.")
    return redirect("portal:admin_banners")


# ---- Feature ----


@admin_required
def admin_features(request):
    return _admin_shell(
        request,
        "portal/admin/features.html",
        {"items": Feature.objects.all()},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_feature_create(request):
    form = FeatureForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Afzallik yaratildi.")
        return redirect("portal:admin_features")
    return _admin_shell(
        request,
        "portal/admin/feature_form.html",
        {"form": form, "title": "Yangi afzallik"},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_feature_edit(request, pk):
    obj = get_object_or_404(Feature, pk=pk)
    form = FeatureForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Afzallik yangilandi.")
        return redirect("portal:admin_features")
    return _admin_shell(
        request,
        "portal/admin/feature_form.html",
        {"form": form, "title": "Afzallik tahrirlash", "obj": obj},
    )


@admin_required
@require_http_methods(["POST"])
def admin_feature_delete(request, pk):
    obj = get_object_or_404(Feature, pk=pk)
    obj.delete()
    messages.success(request, "Afzallik o‘chirildi.")
    return redirect("portal:admin_features")


# ---- News ----


@admin_required
def admin_news(request):
    return _admin_shell(
        request,
        "portal/admin/news_list.html",
        {"items": News.objects.all()},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_news_create(request):
    form = NewsForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Yangilik yaratildi.")
        return redirect("portal:admin_news")
    return _admin_shell(
        request,
        "portal/admin/news_form.html",
        {"form": form, "title": "Yangi yangilik"},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_news_edit(request, pk):
    obj = get_object_or_404(News, pk=pk)
    form = NewsForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Yangilik yangilandi.")
        return redirect("portal:admin_news")
    return _admin_shell(
        request,
        "portal/admin/news_form.html",
        {"form": form, "title": "Yangilik tahrirlash", "obj": obj},
    )


@admin_required
@require_http_methods(["POST"])
def admin_news_delete(request, pk):
    obj = get_object_or_404(News, pk=pk)
    obj.delete()
    messages.success(request, "Yangilik o‘chirildi.")
    return redirect("portal:admin_news")


# ---- FAQ ----


@admin_required
def admin_faqs(request):
    return _admin_shell(
        request,
        "portal/admin/faqs.html",
        {"items": FAQ.objects.all()},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_faq_create(request):
    form = FAQForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "FAQ yaratildi.")
        return redirect("portal:admin_faqs")
    return _admin_shell(
        request,
        "portal/admin/faq_form.html",
        {"form": form, "title": "Yangi FAQ"},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def admin_faq_edit(request, pk):
    obj = get_object_or_404(FAQ, pk=pk)
    form = FAQForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "FAQ yangilandi.")
        return redirect("portal:admin_faqs")
    return _admin_shell(
        request,
        "portal/admin/faq_form.html",
        {"form": form, "title": "FAQ tahrirlash", "obj": obj},
    )


@admin_required
@require_http_methods(["POST"])
def admin_faq_delete(request, pk):
    obj = get_object_or_404(FAQ, pk=pk)
    obj.delete()
    messages.success(request, "FAQ o‘chirildi.")
    return redirect("portal:admin_faqs")


# ---- Leads ----


@admin_required
def admin_leads(request):
    return _admin_shell(
        request,
        "portal/admin/leads.html",
        {"leads": Lead.objects.all()},
    )


@admin_required
@require_http_methods(["POST"])
def admin_lead_toggle(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    lead.is_contacted = not lead.is_contacted
    lead.save(update_fields=["is_contacted"])
    state = "bog‘lanilgan" if lead.is_contacted else "yangi"
    messages.success(request, f"Ariza holati: {state}.")
    return redirect("portal:admin_leads")


@admin_required
@require_http_methods(["POST"])
def admin_lead_delete(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    lead.delete()
    messages.success(request, "Ariza o‘chirildi.")
    return redirect("portal:admin_leads")
