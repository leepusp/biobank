from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from .sample import Sample


class Event(models.Model):
    """
    Evento relacionado ao ciclo de vida de uma amostra.
    Usado para auditoria, rastreabilidade e histórico.
    """

    EVENT_TYPES = [
        ("entry", "Entrada"),
        ("freeze", "Congelamento"),
        ("thaw", "Descongelamento"),
        ("transfer", "Transferência"),
    ]

    # =========================
    # VÍNCULO
    # =========================
    sample = models.ForeignKey(
        Sample,
        on_delete=models.CASCADE,
        related_name="events",
    )

    # =========================
    # DADOS DO EVENTO
    # =========================
    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPES,
    )

    timestamp = models.DateTimeField(
        default=timezone.now,
    )

    notes = models.TextField(
        blank=True,
        null=True,
    )

    # =========================
    # AUDITORIA
    # =========================
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sample_events",
        help_text="Usuário que realizou o evento",
    )

    # =========================
    # REPRESENTAÇÃO
    # =========================
    def __str__(self):
        return f"{self.sample} – {self.get_event_type_display()}"
