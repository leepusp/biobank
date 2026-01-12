from django.db import models
from django.contrib.auth.models import User

from .biobank import Biobank
from .tags import Tag
from .keywords import KeywordValue
from .collection_user_role import CollectionUserRole


class Collection(models.Model):
    """
    Coleção científica pertencente a um Biobank.
    Controla acesso, visibilidade e governança de amostras.
    """

    # =========================
    # METADADOS BÁSICOS
    # =========================
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    biobank = models.ForeignKey(
        Biobank,
        on_delete=models.CASCADE,
        related_name="collections",
    )

    # =========================
    # GOVERNANÇA / PERMISSÕES
    # =========================
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="owned_collections",
        help_text="Responsável científico pela coleção",
    )

    VISIBILITY_CHOICES = [
        ("private", "Privada"),
        ("group", "Grupo de pesquisa"),
        ("biobank", "Biobank"),
        ("public", "Pública"),
    ]

    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default="private",
        help_text="Define quem pode visualizar esta coleção",
    )

    # =========================
    # CICLO DE VIDA
    # =========================
    is_active = models.BooleanField(
        default=True,
        help_text="Indica se a Collection está ativa para uso",
    )

    # (FUTURO PRÓXIMO)
    # research_group = models.ForeignKey(
    #     "ResearchGroup",
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL,
    #     related_name="collections",
    # )

    # =========================
    # CLASSIFICAÇÃO
    # =========================
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="collections",
    )

    keywords = models.ManyToManyField(
        KeywordValue,
        blank=True,
        related_name="collections",
    )

    # =========================
    # PAPÉIS LOCAIS (ACL LEVE)
    # =========================
    members = models.ManyToManyField(
        User,
        through="core.CollectionUserRole",
        related_name="collections",
        blank=True,
    )

    # =========================
    # REPRESENTAÇÃO
    # =========================
    def __str__(self):
        return self.name

    # =========================
    # CONVENIÊNCIA / ADMIN
    # =========================
    @property
    def owner_users(self):
        """
        Retorna todos os usuários com papel OWNER nesta coleção.
        """
        return [
            ur.user
            for ur in self.user_roles.filter(
                role=CollectionUserRole.OWNER
            )
        ]

    def owners_display(self):
        owners = self.owner_users
        return ", ".join(u.username for u in owners) if owners else "-"

    owners_display.short_description = "Orientador(es)"
