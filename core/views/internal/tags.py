# core/views/tags.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

from core.context import base_context
from core.models import Tag, KeywordValue
from core.forms import TagForm


# ============================================================
# TAG SEARCH (reutiliza a tela de tags)
# ============================================================
def search_view(request):
    ctx = base_context(request)

    query = (request.GET.get("q") or "").strip().lower()
    tag_id = request.GET.get("tag")
    kv_id = request.GET.get("kv")

    biobanks = ctx.get("biobanks", [])
    collections = ctx.get("collections", [])
    samples = ctx.get("samples", [])

    selected_tag = Tag.objects.filter(id=tag_id).first() if tag_id else None
    selected_kv = KeywordValue.objects.filter(id=kv_id).first() if kv_id else None

    if selected_tag:
        biobanks = biobanks.filter(tags=selected_tag)

    if selected_kv:
        samples = samples.filter(keyword_values=selected_kv)

    if query:
        biobanks = [
            b for b in biobanks
            if query in b.name.lower()
            or any(query in t.name.lower() for t in b.tags.all())
        ]

        collections = [
            c for c in collections
            if query in c.name.lower()
        ]

        samples = [
            s for s in samples
            if query in s.sample_id.lower()
            or any(query in kv.value.lower() for kv in s.keyword_values.all())
        ]

    ctx["selected_tag"] = selected_tag
    ctx["selected_keyword_value"] = selected_kv
    ctx["search_results"] = {
        "biobanks": list(biobanks),
        "collections": list(collections),
        "samples": list(samples),
    }

    return render(
        request,
        "internal/tags/tags.html",
        ctx
    )


# ============================================================
# TAG LIST / MANAGE  (/?page=tags)
# ============================================================
def tags_view(request):
    if not request.user.is_authenticated:
        raise PermissionDenied

    ctx = base_context(request)

    enriched = []
    for tag in Tag.objects.all().order_by("name"):
        biobanks = list(tag.biobanks.all())
        collections = list(tag.collections.all())
        samples = list(tag.samples.all())

        enriched.append({
            "tag": tag,
            "biobanks": biobanks,
            "collections": collections,
            "samples": samples,
            "biobank_count": len(biobanks),
            "collection_count": len(collections),
            "sample_count": len(samples),
            "total_use": len(biobanks) + len(collections) + len(samples),
        })

    ctx["tags"] = enriched
    ctx["is_admin"] = request.user.is_superuser

    return render(
        request,
        "internal/tags/tags.html",
        ctx
    )


# ============================================================
# CREATE TAG (POST – NÃO AJAX)
# ============================================================
def create_tag_view(request):
    if request.method != "POST":
        return redirect("/?page=tags")

    name = (request.POST.get("name") or "").strip()

    if not name:
        messages.error(request, "Tag name cannot be empty.")
        return redirect("/?page=tags")

    existing = Tag.objects.filter(name__iexact=name).first()
    if existing:
        messages.info(request, f"Tag '{name}' already exists.")
        return redirect("/?page=tags")

    Tag.objects.create(name=name)
    messages.success(request, "Tag created successfully!")

    return redirect("/?page=tags")


# ============================================================
# CREATE TAG (AJAX – usado no Biobank)
# ============================================================
def create_tag_ajax_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    name = (request.POST.get("name") or "").strip()
    if not name:
        return JsonResponse(
            {"success": False, "error": "Tag name cannot be empty."},
            status=400
        )

    existing = Tag.objects.filter(name__iexact=name).first()
    if existing:
        return JsonResponse({
            "success": True,
            "id": existing.id,
            "name": existing.name,
            "reused": True,
        })

    tag = Tag.objects.create(name=name)

    return JsonResponse({
        "success": True,
        "id": tag.id,
        "name": tag.name,
        "reused": False,
    })


# ============================================================
# EDIT TAG
# ============================================================
def edit_tag_view(request):
    if request.method != "POST":
        return redirect("/?page=tags")

    tag = Tag.objects.filter(id=request.POST.get("id")).first()
    if not tag:
        messages.error(request, "Tag not found.")
        return redirect("/?page=tags")

    form = TagForm(request.POST, instance=tag)
    if form.is_valid():
        form.save()
        messages.success(request, "Tag updated successfully!")
    else:
        messages.error(request, "Invalid tag data.")

    return redirect("/?page=tags")


# ============================================================
# DELETE TAG
# ============================================================
def delete_tag_view(request):
    if request.method != "POST":
        return redirect("/?page=tags")

    tag = Tag.objects.filter(id=request.POST.get("id")).first()
    if not tag:
        messages.error(request, "Tag not found.")
        return redirect("/?page=tags")

    total_use = (
        tag.biobanks.count()
        + tag.collections.count()
        + tag.samples.count()
    )

    if total_use > 0 and not request.user.is_superuser:
        messages.error(
            request,
            f"This tag is used in {total_use} places and cannot be deleted."
        )
        return redirect("/?page=tags")

    tag.delete()
    messages.success(request, "Tag deleted successfully!")

    return redirect("/?page=tags")
