from django.db import models


class PatientSource(models.Model):
    """Modèle pour les sources/canaux de recommandation des patients"""
    
    name = models.CharField(
        "Nom",
        max_length=100,
        unique=True,
        help_text="Ex: Réseaux sociaux, Recommandation, Publicité"
    )
    code = models.CharField(
        "Code",
        max_length=20,
        unique=True,
        help_text="Code court pour identification"
    )
    description = models.TextField(
        "Description",
        blank=True,
        null=True
    )
    color = models.CharField(
        "Couleur",
        max_length=7,
        default="#007bff",
        help_text="Code couleur hexadécimal (ex: #007bff)"
    )
    icon = models.CharField(
        "Icône",
        max_length=50,
        blank=True,
        null=True,
        help_text="Classe d'icône Font Awesome (ex: fas fa-share-alt)"
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
        verbose_name = "Source de patient"
        verbose_name_plural = "Sources de patients"
        ordering = ['name']
    
    def __str__(self):
        return self.name

