from django.db import models
from .employee import Employee


class MedicalVisit(models.Model):
    """
    Modèle pour les visites médicales des employés
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='medical_visits',
        verbose_name='Employé'
    )
    
    doctor_name = models.CharField(
        max_length=255,
        verbose_name='Nom du médecin'
    )
    
    visit_date = models.DateField(
        verbose_name='Date de visite'
    )
    
    result_file = models.FileField(
        upload_to='hr_media/medical_results/',
        null=True,
        blank=True,
        verbose_name='Résultat de visite (PDF)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Visite médicale'
        verbose_name_plural = 'Visites médicales'
        ordering = ['-visit_date', '-created_at']
        
    def __str__(self):
        return f"Visite médicale de {self.employee} le {self.visit_date}"
