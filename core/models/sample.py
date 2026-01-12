from django.db import models
from django.contrib.auth.models import User

from .collection import Collection
from .biobank import Biobank
from .tags import Tag
from .keywords import KeywordValue


class Sample(models.Model):
    """
    Amostra biológica armazenada no Biobank.

    Hierarquia:
    Biobank → Collection → Sample
    """

    # =========================
    # IDENTIFICAÇÃO
    # =========================
    sample_id = models.CharField(max_length=100, unique=True)

    sample_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    organism_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    # =========================
    # VÍNCULOS HIERÁRQUICOS
    # =========================
    collection = models.ForeignKey(
        Collection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="samples",
    )

    biobank = models.ForeignKey(
        Biobank,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="samples",
    )

    # =========================
    # GOVERNANÇA / PERMISSÕES
    # =========================
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="owned_samples",
        help_text="Responsável pela amostra",
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
        help_text="Define quem pode visualizar esta amostra",
    )

    # =========================
    # CICLO DE VIDA (SOFT DELETE)
    # =========================
    is_active = models.BooleanField(
        default=True,
        help_text="Indica se a Sample está ativa para uso",
    )

    # =========================
    # METADADOS
    # =========================
    storage_location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    notes = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    # =========================
    # CLASSIFICAÇÃO
    # =========================
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="samples",
    )

    keyword_values = models.ManyToManyField(
        KeywordValue,
        blank=True,
        related_name="samples",
    )

    # =========================
    # LÓGICA DE PERSISTÊNCIA
    # =========================
    def save(self, *args, **kwargs):
        """
        - Herda automaticamente o biobank da collection
        - Move arquivos quando a amostra é vinculada a uma collection
        """
        from .sample_files import move_sample_files

        old_collection_id = None
        if self.pk:
            old_collection_id = (
                Sample.objects.filter(pk=self.pk)
                .values_list("collection_id", flat=True)
                .first()
            )

        # Regra de herança do biobank
        if self.collection:
            self.biobank = self.collection.biobank
        else:
            self.biobank = None

        super().save(*args, **kwargs)

        # Move arquivos somente quando a amostra é vinculada pela primeira vez
        if self.collection and old_collection_id is None:
            move_sample_files(self)

    # =========================
    # REPRESENTAÇÃO
    # =========================
    def __str__(self):
        return self.sample_id
