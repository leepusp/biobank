# core/views/internal/samples.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import PermissionDenied

from core.context import base_context

from core.models import (
    Sample,
    Collection,
    SampleFile,
    Tag,
    Keyword,
    KeywordValue,
)

from core.permissions.samples import (
    can_view_sample,
    can_edit_sample,
    can_delete_sample,
)
from core.permissions.collections import can_edit_collection


def samples_view(request):
    """
    Internal view for managing Samples.
    Includes creation, update, soft-deactivation and (admin-only) deletion.
    """

    user = request.user
    action = request.POST.get("action") if request.method == "POST" else None

    # =========================================================
    # CREATE SAMPLE
    # =========================================================
    if action == "add_sample":

        if not user.is_authenticated:
            raise PermissionDenied

        with transaction.atomic():

            collection_id = request.POST.get("collection") or None
            collection = None

            if collection_id:
                collection = get_object_or_404(Collection, id=collection_id)

                # Permissão herdada da Collection
                if not can_edit_collection(user, collection):
                    raise PermissionDenied

            sample = Sample.objects.create(
                sample_id=request.POST.get("sample_id"),
                organism_name=request.POST.get("organism_name"),
                collection=collection,
                sample_type=request.POST.get("sample_type"),
                storage_location=request.POST.get("storage_location"),
                notes=request.POST.get("notes"),
                owner=user,   # governança
                is_active=True,
            )

            # TAGS
            tag_ids = request.POST.getlist("tags")
            if tag_ids:
                sample.tags.set(tag_ids)

            # KEYWORDS
            for raw in request.POST.getlist("keyword_pairs"):
                if ":::" not in raw:
                    continue

                key, value = raw.split(":::")
                keyword, _ = Keyword.objects.get_or_create(
                    name=key.strip()
                )
                kv, _ = KeywordValue.objects.get_or_create(
                    keyword=keyword,
                    value=value.strip()
                )
                sample.keyword_values.add(kv)

            # FILES
            for index, f in enumerate(request.FILES.getlist("file")):
                SampleFile.objects.create(
                    sample=sample,
                    file=f,
                    description=request.POST.get(
                        f"file_description_{index}", ""
                    ),
                    file_type=request.POST.get(
                        f"file_type_{index}", ""
                    ),
                )

        messages.success(request, "Sample criada com sucesso!")
        return redirect("/?page=samples")

    # =========================================================
    # UPDATE SAMPLE COLLECTION
    # =========================================================
    elif action == "update_sample_collection":

        sample = get_object_or_404(
            Sample, id=request.POST.get("sample_id")
        )

        if not can_edit_sample(user, sample):
            raise PermissionDenied

        collection_id = request.POST.get("collection") or None

        if collection_id:
            collection = get_object_or_404(Collection, id=collection_id)

            if not can_edit_collection(user, collection):
                raise PermissionDenied

            sample.collection = collection
        else:
            sample.collection = None

        sample.save()
        messages.success(
            request, "Collection da Sample atualizada com sucesso!"
        )
        return redirect("/?page=samples")

    # =========================================================
    # DEACTIVATE SAMPLE (SOFT DELETE)
    # =========================================================
    elif action == "deactivate_sample":

        sample = get_object_or_404(
            Sample, id=request.POST.get("sample_id")
        )

        if not can_edit_sample(user, sample):
            raise PermissionDenied

        sample.is_active = False
        sample.save(update_fields=["is_active"])

        messages.success(
            request, "Sample desativada com sucesso."
        )
        return redirect("/?page=samples")

    # =========================================================
    # DELETE SAMPLE (HARD DELETE – ADMIN ONLY)
    # =========================================================
    elif action == "delete_sample":

        sample = get_object_or_404(
            Sample, id=request.POST.get("sample_id")
        )

        if not (user.is_superuser or user.is_staff):
            raise PermissionDenied

        sample.delete()
        messages.success(
            request, "Sample removida permanentemente."
        )
        return redirect("/?page=samples")

    # =========================================================
    # GET — LIST / FILTER / SEARCH
    # =========================================================
    ctx = base_context(request)

    # Only active samples
    samples = Sample.objects.filter(is_active=True)

    # Filtrar por permissão de visualização
    samples = [
        s for s in samples
        if can_view_sample(user, s)
    ]

    col_id = request.GET.get("collection")
    if col_id:
        samples = [
            s for s in samples
            if s.collection_id == int(col_id)
        ]
        ctx["selected_collection"] = Collection.objects.filter(
            id=col_id
        ).first()

    search = (request.GET.get("squery") or "").strip()
    if search:
        samples = [
            s for s in samples
            if (
                search.lower() in (s.sample_id or "").lower()
                or search.lower() in (s.organism_name or "").lower()
                or s.keyword_values.filter(
                    value__icontains=search
                ).exists()
            )
        ]

    # ---------------------------------------------------------
    # FLAGS DE PERMISSÃO PARA TEMPLATE
    # ---------------------------------------------------------
    for s in samples:
        s.can_edit = can_edit_sample(user, s)
        s.can_delete = (
            user.is_superuser or user.is_staff
        )

    ctx["samples"] = samples
    ctx["collections"] = Collection.objects.filter(
        is_active=True
    ).order_by("name")
    ctx["all_tags"] = Tag.objects.all().order_by("name")

    return render(
        request,
        "internal/samples/samples.html",
        ctx
    )

