from django.db import models


class DocumentType(models.Model):
    """Modèle pour les types de documents médicaux"""
    
    name = models.CharField(
        "Nom",
        max_length=100,
        unique=True
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
        verbose_name = "Type de document"
        verbose_name_plural = "Types de documents"
        ordering = ['name']
    
    def __str__(self):
        return self.name

