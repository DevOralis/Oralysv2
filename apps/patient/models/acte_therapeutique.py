from django.db import models


class ActeTherapeutique(models.Model):
    """Modèle pour les actes médicaux et thérapeutiques"""
    
    libelle = models.CharField(
        "Libellé",
        max_length=255,
        unique=True
    )
    description = models.TextField(
        "Description",
        blank=True,
        null=True
    )
    price = models.DecimalField(
        "Prix",
        max_digits=10,
        decimal_places=2
    )
    duration = models.PositiveIntegerField(
        "Durée (minutes)",
        blank=True,
        null=True,
        help_text="Durée approximative de l'acte"
    )
    is_active = models.BooleanField(
        "Actif",
        default=True
    )
    created_at = models.DateTimeField(
        "Date de création",
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        "Date de modification",
        auto_now=True
    )
    
    class Meta:
        verbose_name = "Acte thérapeutique"
        verbose_name_plural = "Actes thérapeutiques"
        ordering = ['libelle']
    
    def __str__(self):
        return self.libelle

