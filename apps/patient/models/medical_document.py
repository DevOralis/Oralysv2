from django.db import models
from .patient import Patient
from .document_type import DocumentType


class MedicalDocument(models.Model):
    """Modèle pour stocker les documents médicaux des patients"""
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='medical_documents',
        verbose_name="Patient"
    )
    document_type = models.ForeignKey(
        DocumentType,
        on_delete=models.PROTECT,
        related_name='medical_documents',
        verbose_name="Type de document",
        help_text="Type de document (géré depuis la page Paramètres)"
    )
    document_file = models.FileField(
        "Fichier",
        upload_to='medical_documents/%Y/%m/%d/',
        help_text="Document médical du patient"
    )
    uploaded_at = models.DateTimeField(
        "Date d'ajout",
        auto_now_add=True
    )
    description = models.CharField(
        "Description",
        max_length=255,
        blank=True,
        null=True,
        help_text="Description optionnelle du document"
    )
    
    class Meta:
        verbose_name = "Document médical"
        verbose_name_plural = "Documents médicaux"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.document_type.name} - {self.patient.get_full_name()}"
    
    @property
    def file_name(self):
        """Retourne le nom du fichier"""
        import os
        return os.path.basename(self.document_file.name) if self.document_file else ''


