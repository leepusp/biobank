# core/permissions/samples.py

from core.models import Sample, CollectionUserRole
from core.permissions.collections import (
    can_view_collection,
    can_edit_collection,
    can_manage_collection_permissions,
)


# ===========================================================
# VISUALIZAÇÃO
# ===========================================================

def can_view_sample(user, sample: Sample) -> bool:
    """
    Define se um usuário pode visualizar uma Sample.

    Regras:
    - Sample com Collection → herda permissões da Collection
    - Sample sem Collection →
        - criador da sample
        - coordenadores (OWNER)
    """

    if not sample or not user.is_authenticated:
        return False

    # -------------------------------------------------------
    # SAMPLE SEM COLLECTION (rascunho)
    # -------------------------------------------------------
    if not sample.collection:

        # Criador da sample
        if sample.owner == user:
            return True

        # Coordenador (OWNER)
        return CollectionUserRole.objects.filter(
            user=user,
            role=CollectionUserRole.OWNER,
        ).exists()

    # -------------------------------------------------------
    # SAMPLE COM COLLECTION
    # -------------------------------------------------------
    return can_view_collection(user, sample.collection)


# ===========================================================
# EDIÇÃO
# ===========================================================

def can_edit_sample(user, sample: Sample) -> bool:
    """
    Define se um usuário pode editar uma Sample.
    """

    if not sample or not user.is_authenticated:
        return False

    # -------------------------------------------------------
    # SAMPLE SEM COLLECTION
    # -------------------------------------------------------
    if not sample.collection:
        return (
            sample.owner == user
            or CollectionUserRole.objects.filter(
                user=user,
                role=CollectionUserRole.OWNER,
            ).exists()
        )

    # -------------------------------------------------------
    # SAMPLE COM COLLECTION
    # -------------------------------------------------------
    return can_edit_collection(user, sample.collection)


# ===========================================================
# EXCLUSÃO
# ===========================================================

def can_delete_sample(user, sample: Sample) -> bool:
    """
    Define se um usuário pode deletar uma Sample.
    """

    if not sample or not user.is_authenticated:
        return False

    # -------------------------------------------------------
    # SAMPLE SEM COLLECTION
    # -------------------------------------------------------
    if not sample.collection:
        # Apenas coordenadores (OWNER)
        return CollectionUserRole.objects.filter(
            user=user,
            role=CollectionUserRole.OWNER,
        ).exists()

    # -------------------------------------------------------
    # SAMPLE COM COLLECTION
    # -------------------------------------------------------
    return can_manage_collection_permissions(user, sample.collection)

