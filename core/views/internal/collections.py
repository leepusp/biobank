# core/views/internal/collections.py

from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.db import transaction
from django.core.exceptions import PermissionDenied

from core.context import base_context
from core.forms import CollectionForm

from core.models import (
    Collection,
    CollectionUserRole,
    Tag,
    Keyword,
    KeywordValue,
)

from core.permissions.collections import (
    can_view_collection,
    can_edit_collection,
    can_manage_collection_permissions,
)


def collections_view(request):
    """
    Internal view for managing Collections.
    Includes creation, soft-deactivation and (admin-only) deletion.
    """

    user = request.user
    action = request.POST.get("action") if request.method == "POST" else None

    # ============================================================
    # CREATE COLLECTION
    # ============================================================
    if action == "add_collection":

        if not user.is_authenticated:
            raise PermissionDenied

        form = CollectionForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():

                    # ------------------------------------------------
                    # 1) Create Collection
                    # ------------------------------------------------
                    collection = form.save(commit=False)
                    collection.owner = user
                    collection.is_active = True
                    collection.save()

                    # ACL: OWNER científico
                    CollectionUserRole.objects.create(
                        user=user,
                        collection=collection,
                        role=CollectionUserRole.OWNER
                    )

                    # ------------------------------------------------
                    # 2) TAGS
                    # ------------------------------------------------
                    selected_tags = request.POST.getlist("tags")
                    if selected_tags:
                        collection.tags.set(selected_tags)

                    # ------------------------------------------------
                    # 3) KEYWORDS
                    # ------------------------------------------------
                    pairs = request.POST.getlist("keyword_pairs")

                    for raw in pairs:
                        if ":::" not in raw:
                            continue

                        key, value = raw.split(":::")
                        key = key.strip()
                        value = value.strip()

                        if not key or not value:
                            continue

                        keyword_obj, _ = Keyword.objects.get_or_create(
                            name=key
                        )

                        kv, _ = KeywordValue.objects.get_or_create(
                            keyword=keyword_obj,
                            value=value
                        )

                        collection.keywords.add(kv)

                    messages.success(
                        request,
                        "Collection criada com sucesso!"
                    )
                    return redirect("/?page=collections")

            except Exception as e:
                messages.error(
                    request,
                    f"Erro ao criar Collection: {e}"
                )
                return redirect("/?page=collections")

        else:
            messages.error(request, "Dados inválidos.")
            return redirect("/?page=collections")

    # ============================================================
    # DEACTIVATE COLLECTION (SOFT DELETE)
    # ============================================================
    elif action == "deactivate_collection":

        cid = request.POST.get("collection_id")
        collection = get_object_or_404(Collection, id=cid)

        if not can_manage_collection_permissions(user, collection):
            raise PermissionDenied

        collection.is_active = False
        collection.save(update_fields=["is_active"])

        messages.success(
            request,
            "Collection desativada com sucesso."
        )
        return redirect("/?page=collections")

    # ============================================================
    # DELETE COLLECTION (HARD DELETE – ADMIN ONLY)
    # ============================================================
    elif action == "delete_collection":

        if not (user.is_superuser or user.is_staff):
            raise PermissionDenied

        cid = request.POST.get("collection_id")
        collection = get_object_or_404(Collection, id=cid)

        collection.delete()

        messages.success(
            request,
            "Collection removida permanentemente."
        )
        return redirect("/?page=collections")

    # ============================================================
    # FORM DEFAULT (GET)
    # ============================================================
    else:
        # Preselect biobank if coming from ?biobank=ID
        initial = {}
        biobank_id = request.GET.get("biobank")
        if biobank_id:
            initial["biobank"] = biobank_id

        form = CollectionForm(initial=initial)

    # ============================================================
    # CONTEXT BASE
    # ============================================================
    ctx = base_context(request)
    ctx["collection_form"] = form
    ctx["all_tags"] = Tag.objects.all().order_by("name")

    # Tag recém criada via modal
    ctx["preselect_tag"] = request.session.pop(
        "new_tag_id",
        None
    )

    # ============================================================
    # LISTAGEM COM PERMISSÕES (ACTIVE ONLY)
    # ============================================================
    collections = Collection.objects.filter(is_active=True)

    # Optional filter by biobank
    biobank_id = request.GET.get("biobank")
    if biobank_id:
        collections = collections.filter(biobank_id=biobank_id)

    visible_collections = []

    for c in collections:
        if can_view_collection(user, c):
            c.can_edit = can_edit_collection(user, c)
            c.can_manage_members = can_manage_collection_permissions(user, c)

            # Members (read-only)
            c.members_roles = (
                c.user_roles
                .select_related("user")
                .all()
            )

            visible_collections.append(c)

    ctx["collections"] = visible_collections

    return render(
        request,
        "internal/collections/collections.html",
        ctx
    )
