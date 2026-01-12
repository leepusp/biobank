# core/views/context.py

from django.db.models import Q

from core.models import (
    Biobank,
    Collection,
    Sample,
    CollectionUserRole,
    Tag,
    Keyword,
    KeywordValue,
)

from core.forms import BiobankForm, CollectionForm


def base_context(request, public: bool = False):
    """
    Contexto base compartilhado entre interface interna (LIMS)
    e interface pública.
    """

    user = request.user

    # ======================================================
    # CONTEXTO PÚBLICO
    # ======================================================
    if public:
        return {
            "request": request,
            "user": user,
            "is_public": True,
        }

    # ======================================================
    # CONTEXTO INTERNO (LIMS)
    # ======================================================

    # ----- All keywords (global listing) -----
    all_keywords = Keyword.objects.all().order_by("name")

    # ----- Collections and samples visible to user -----
    if user.is_superuser:
        collections = Collection.objects.all()
        samples = Sample.objects.all()
    else:
        collections = Collection.objects.filter(
            user_roles__user=user
        ).distinct()

        samples = Sample.objects.filter(
            Q(collection__user_roles__user=user)
            | Q(collection__isnull=True)
        ).distinct()

    # ----- Biobanks (active only) -----
    biobanks = Biobank.objects.filter(is_active=True)

    # ----- Detect if user is OWNER of any collection -----
    is_owner_of_any = CollectionUserRole.objects.filter(
        user=user,
        role=CollectionUserRole.OWNER
    ).exists()

    can_manage_permissions = user.is_superuser or is_owner_of_any

    return {
        # request / state
        "request": request,
        "user": user,
        "is_public": False,

        # entities
        "biobanks": biobanks,
        "collections": collections,
        "samples": samples,

        # metadata
        "all_keywords": all_keywords,

        # forms (injected later by views)
        "biobank_form": None,
        "collection_form": None,
        "sample_form": None,

        # permissions
        "can_manage_permissions": can_manage_permissions,

        # state for detail pages
        "selected_collection": None,
    }
