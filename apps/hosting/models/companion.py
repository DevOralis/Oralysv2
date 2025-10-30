from django.db import models
from apps.patient.models import Patient
from .room import Room
from .bed import Bed
from decimal import Decimal

class Companion(models.Model):
    companion_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='companions')
    companion_name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True, related_name='companions')
    bed = models.ForeignKey(Bed, on_delete=models.CASCADE, null=True, blank=True, related_name='companions')
    accommodation_start_date = models.DateField(null=True, blank=True)
    accommodation_end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Companion"
        verbose_name_plural = "Companions"

    def __str__(self):
        return f"{self.companion_name} (Companion of {self.patient})"
    
    @property
    def nb_jours_acc(self):
        """Calcule le nombre de jours d'accompagnement"""
        if self.accommodation_start_date and self.accommodation_end_date:
            nb_jours = (self.accommodation_end_date - self.accommodation_start_date).days
            return nb_jours if nb_jours > 0 else 1
        return 0
    
    @property
    def acte_accompagnant(self):
        """Récupère l'acte accompagnant avec son prix"""
        try:
            from apps.patient.models.acte import Acte
            return Acte.objects.get(libelle__icontains='Accompagnant')
        except:
            return None
    
    @property
    def cout_total(self):
        """Calcule le coût total de l'accompagnement"""
        if self.nb_jours_acc > 0:
            if self.acte_accompagnant:
                return self.acte_accompagnant.price * self.nb_jours_acc
            else:
                # Prix par défaut si acte non trouvé
                return Decimal('50.00') * self.nb_jours_acc
        return Decimal('0.00')