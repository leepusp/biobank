# core/permissions/biobanks.py

from core.models import Biobank, BiobankUserRole


# ===========================================================
# HELPERS
# ===========================================================

def _is_admin(user) -> bool:
    return user.is_authenticated and (user.is_superuser or user.is_staff)


def _get_biobank_role(user, biobank):
    """
    Retorna o papel do usuário no Biobank ou None.
    Admin técnico é tratado como OWNER.
    """
    if not user.is_authenticated:
        return None

    if _is_admin(user):
        return BiobankUserRole.OWNER

    return (
        BiobankUserRole.objects
        .filter(user=user, biobank=biobank)
        .values_list("role", flat=True)
        .first()
    )


# ===========================================================
# VISUALIZAÇÃO
# ===========================================================

def can_view_biobank(user, biobank: Biobank) -> bool:
    """
    Define se um usuário pode visualizar um Biobank
    (contexto da interface interna).
    """

    # Biobank desativado nunca é visível
    if not biobank.is_active:
        return False

    # Interface interna exige login
    if not user.is_authenticated:
        return False

    # Público (qualquer usuário autenticado)
    if biobank.visibility == "public":
        return True

    # Privado → apenas owner
    if biobank.visibility == "private":
        return user == biobank.owner

    # Restrito ao Biobank → precisa ter papel
    role = _get_biobank_role(user, biobank)
    return role is not None


# ===========================================================
# EDIÇÃO
# ===========================================================

def can_edit_biobank(user, biobank: Biobank) -> bool:
    """
    Define se um usuário pode editar dados do Biobank.
    """

    if not user.is_authenticated:
        return False

    if not biobank.is_active:
        return False

    # Admin técnico
    if _is_admin(user):
        return True

    return BiobankUserRole.objects.filter(
        user=user,
        biobank=biobank,
        role__in=[
            BiobankUserRole.OWNER,
            BiobankUserRole.MANAGER,
        ],
    ).exists()


# ===========================================================
# GERENCIAMENTO DE MEMBROS
# ===========================================================

def can_manage_biobank_permissions(user, biobank: Biobank) -> bool:
    """
    Define se o usuário pode gerenciar membros do Biobank.
    """

    if not user.is_authenticated:
        return False

    if not biobank.is_active:
        return False

    # Admin técnico sempre pode
    if _is_admin(user):
        return True

    # Apenas OWNER científico
    return BiobankUserRole.objects.filter(
        user=user,
        biobank=biobank,
        role=BiobankUserRole.OWNER,
    ).exists()
