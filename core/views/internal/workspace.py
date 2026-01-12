from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# =========================================================
# CONTEXTO GLOBAL
# =========================================================
from core.context import base_context

# =========================================================
# INTERNAL ENTITY VIEWS
# =========================================================
from core.views.internal.biobanks.biobanks import biobanks_view
from core.views.internal.collections import collections_view
from core.views.internal.samples import samples_view

# =========================================================
# TAGS
# =========================================================
from core.views.internal.tags import (
    tags_view,
    create_tag_view,
    edit_tag_view,
    delete_tag_view,
)

# =========================================================
# KEYWORDS
# =========================================================
from core.views.internal.keywords import (
    keywords_view,
    edit_keyword_view,
    delete_keyword_view,
)

# =========================================================
# WORKSPACE (HOME INTERNO / ENTRYPOINT DO LIMS)
# =========================================================
@login_required
def home(request):
    """
    Entry point do ambiente interno (Workspace).
    Controla navegação via ?page=
    """

    page = request.GET.get("page", "workspace")

    ROUTES = {
        # ================= MAIN =================
        "workspace": workspace_view,
        "biobanks": biobanks_view,
        "collections": collections_view,
        "samples": samples_view,

        # ================= TAGS =================
        "tags": tags_view,
        "add_tag": create_tag_view,
        "edit_tag": edit_tag_view,
        "delete_tag": delete_tag_view,

        # ================= KEYWORDS =============
        "keywords": keywords_view,
        "edit_keyword": edit_keyword_view,
        "delete_keyword": delete_keyword_view,
    }

    if page in ROUTES:
        return ROUTES[page](request)

    return workspace_view(request)


def workspace_view(request):
    """
    Workspace principal (Dashboard interno do LIMS)
    """
    ctx = base_context(request)

    return render(
        request,
        "internal/workspace/workspace.html",
        ctx
    )
