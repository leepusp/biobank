# core/permissions/collections.py

from core.models import Collection, CollectionUserRole
from core.permissions.biobanks import (
    can_view_biobank,
    can_edit_biobank,
    can_manage_biobank_permissions,
)


# ===========================================================
# VISUALIZAÇÃO
# ===========================================================

def can_view_collection(user, collection: Collection) -> bool:
    """
    Define se um usuário pode visualizar uma Collection.
    """

    # -------------------------------------------------------
    # USUÁRIO NÃO AUTENTICADO
    # -------------------------------------------------------
    if not user.is_authenticated:
        return collection.visibility == "public"

    # -------------------------------------------------------
    # ADMIN TÉCNICO
    # -------------------------------------------------------
    if user.is_superuser or user.is_staff:
        return True

    # -------------------------------------------------------
    # DONO CIENTÍFICO (metadado histórico)
    # -------------------------------------------------------
    if collection.owner == user:
        return True

    # -------------------------------------------------------
    # VISIBILIDADE DIRETA
    # -------------------------------------------------------
    if collection.visibility == "public":
        return True

    # -------------------------------------------------------
    # ACL LOCAL (CollectionUserRole)
    # -------------------------------------------------------
    if CollectionUserRole.objects.filter(
        user=user,
        collection=collection,
    ).exists():
        return True

    # -------------------------------------------------------
    # HERANÇA DO BIOBANK
    # -------------------------------------------------------
    if collection.biobank:
        return can_view_biobank(user, collection.biobank)

    # -------------------------------------------------------
    # FUTURO: GROUP / OUTROS
    # -------------------------------------------------------
    if collection.visibility == "group":
        if hasattr(collection, "research_group") and collection.research_group:
            return collection.research_group in user.research_groups.all()

    return False


# ===========================================================
# EDIÇÃO DE CONTEÚDO
# ===========================================================

def can_edit_collection(user, collection: Collection) -> bool:
    """
    Define se um usuário pode editar dados da Collection
    (metadados, samples, etc).
    """

    if not user.is_authenticated:
        return False

    # -------------------------------------------------------
    # ADMIN TÉCNICO
    # -------------------------------------------------------
    if user.is_superuser or user.is_staff:
        return True

    # -------------------------------------------------------
    # DONO
    # -------------------------------------------------------
    if collection.owner == user:
        return True

    # -------------------------------------------------------
    # PAPÉIS LOCAIS
    # -------------------------------------------------------
    if CollectionUserRole.objects.filter(
        user=user,
        collection=collection,
        role__in=[
            CollectionUserRole.OWNER,
            CollectionUserRole.EDITOR,
        ],
    ).exists():
        return True

    # -------------------------------------------------------
    # HERANÇA DO BIOBANK
    # -------------------------------------------------------
    if collection.biobank:
        return can_edit_biobank(user, collection.biobank)

    return False


# ===========================================================
# GERENCIAMENTO DE MEMBROS / PERMISSÕES
# ===========================================================

def can_manage_collection_permissions(user, collection: Collection) -> bool:
    """
    Define quem pode gerenciar membros e permissões da Collection.
    """

    if not user.is_authenticated:
        return False

    # -------------------------------------------------------
    # ADMIN TÉCNICO
    # -------------------------------------------------------
    if user.is_superuser or user.is_staff:
        return True

    # -------------------------------------------------------
    # COORDENADOR LOCAL (OWNER)
    # -------------------------------------------------------
    if CollectionUserRole.objects.filter(
        user=user,
        collection=collection,
        role=CollectionUserRole.OWNER,
    ).exists():
        return True

    # -------------------------------------------------------
    # HERANÇA DO BIOBANK
    # -------------------------------------------------------
    if collection.biobank:
        return can_manage_biobank_permissions(user, collection.biobank)

    return False

