from django.db import models
from django.contrib.auth.models import User

from .tags import Tag
from .keywords import KeywordValue


class Biobank(models.Model):
    # =========================
    # METADADOS BÁSICOS
    # =========================
    name = models.CharField(max_length=200)
    institution = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    # =========================
    # LOCALIZAÇÃO
    # =========================
    location_label = models.CharField(
        max_length=255,
        blank=True,
        help_text="Human readable location from map search"
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    # =========================
    # NOTAS
    # =========================
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the Biobank"
    )

    # =========================
    # GOVERNANÇA / PERMISSÕES
    # =========================
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="owned_biobanks",
    )

    VISIBILITY_CHOICES = [
        ("private", "Privado"),
        ("biobank", "Restrito ao Biobank"),
        ("public", "Público"),
    ]

    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default="biobank",
    )

    # =========================
    # CICLO DE VIDA
    # =========================
    is_active = models.BooleanField(default=True)

    # =========================
    # CLASSIFICAÇÃO
    # =========================
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="biobanks",
    )

    keywords = models.ManyToManyField(
        KeywordValue,
        blank=True,
        related_name="biobanks",
    )

    def __str__(self):
        return self.name


