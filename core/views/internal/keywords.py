# core/views/keywords.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from core.context import base_context
from core.models import Keyword, KeywordValue


# ============================================================
# KEYWORD LIST / MANAGE  (/?page=keywords)
# ============================================================
def keywords_view(request):
    if not request.user.is_authenticated:
        raise PermissionDenied

    ctx = base_context(request)

    enriched = []

    values_prefetched = KeywordValue.objects.prefetch_related(
        "samples",
        "collections",
        "biobanks"
    )

    for key in Keyword.objects.all().order_by("name"):
        values = values_prefetched.filter(keyword=key)

        sample_count = sum(v.samples.count() for v in values)
        collection_count = sum(v.collections.count() for v in values)
        biobank_count = sum(v.biobanks.count() for v in values)

        enriched.append({
            "keyword": key,
            "values": values,
            "sample_count": sample_count,
            "collection_count": collection_count,
            "biobank_count": biobank_count,
            "total": values.count(),
        })

    ctx["keywords"] = enriched
    ctx["is_admin"] = request.user.is_superuser

    return render(
        request,
        "internal/keywords/keywords.html",
        ctx
    )


# ============================================================
# EDIT KEYWORD
# ============================================================
def edit_keyword_view(request):
    if request.method != "POST":
        return redirect("/?page=keywords")

    key = Keyword.objects.filter(id=request.POST.get("id")).first()
    if not key:
        messages.error(request, "Keyword not found.")
        return redirect("/?page=keywords")

    new_name = (request.POST.get("name") or "").strip()
    if not new_name:
        messages.error(request, "Keyword name cannot be empty.")
        return redirect("/?page=keywords")

    key.name = new_name
    key.save()

    messages.success(request, "Keyword updated successfully!")
    return redirect("/?page=keywords")


# ============================================================
# DELETE KEYWORD
# ============================================================
def delete_keyword_view(request):
    if request.method != "POST":
        return redirect("/?page=keywords")

    key = Keyword.objects.filter(id=request.POST.get("id")).first()
    if not key:
        messages.error(request, "Keyword not found.")
        return redirect("/?page=keywords")

    value_count = KeywordValue.objects.filter(keyword=key).count()

    if value_count > 0 and not request.user.is_superuser:
        messages.error(
            request,
            "This keyword has values associated and cannot be deleted."
        )
        return redirect("/?page=keywords")

    key.delete()
    messages.success(request, "Keyword deleted successfully!")
    return redirect("/?page=keywords")
