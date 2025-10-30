from django.db import models
from apps.pharmacy.models.product import PharmacyProduct


class MedicationPrescription(models.Model):
    """
    Modèle pour gérer les prescriptions de médicaments avec tous les détails
    nécessaires pour une prescription médicale complète.
    """
    
    MOMENT_CHOICES = [
        ('', 'Non spécifié'),
        ('avant_repas', 'Avant les repas'),
        ('apres_repas', 'Après les repas'),
        ('pendant_repas', 'Pendant les repas'),
        ('coucher', 'Au coucher'),
        ('reveil', 'Au réveil'),
        ('douleur', 'En cas de douleur'),
        ('urgence', 'En cas d\'urgence'),
        ('matin', 'Le matin'),
        ('midi', 'À midi'),
        ('soir', 'Le soir'),
        ('quotidien', 'Une fois par jour'),
    ]
    
    FREQUENCE_CHOICES = [
        ('1x', '1 fois par jour'),
        ('2x', '2 fois par jour'),
        ('3x', '3 fois par jour'),
        ('4x', '4 fois par jour'),
        ('6x', '6 fois par jour'),
        ('8x', '8 fois par jour'),
        ('12x', 'Toutes les 12 heures'),
        ('24x', 'Toutes les 24 heures'),
        ('48x', 'Toutes les 48 heures'),
        ('semaine', '1 fois par semaine'),
        ('2semaines', '1 fois toutes les 2 semaines'),
        ('mois', '1 fois par mois'),
        ('as_needed', 'Selon les besoins'),
    ]
    
    consultation = models.ForeignKey('patient.Consultation', on_delete=models.CASCADE, related_name='medication_prescriptions')
    medicament = models.ForeignKey(PharmacyProduct, on_delete=models.CASCADE, verbose_name="Médicament")
    
    # Informations de prescription
    dose = models.CharField(
        max_length=100, 
        verbose_name="Dose",
        help_text="Quantité exacte à administrer à chaque prise (ex: 500mg, 1 comprimé, 5ml)"
    )
    
    frequence = models.CharField(
        max_length=20,
        choices=FREQUENCE_CHOICES,
        verbose_name="Fréquence",
        help_text="Nombre de prises par jour ou intervalle entre deux prises"
    )
    
    duree = models.CharField(
        max_length=50,
        verbose_name="Durée",
        help_text="Période totale du traitement (ex: 7 jours, 2 semaines, 1 mois)"
    )
    
    moment = models.CharField(
        max_length=20,
        choices=MOMENT_CHOICES,
        blank=True,
        verbose_name="Moment de prise",
        help_text="Contexte ou indication spécifique de la prise"
    )
    
    instructions_supplementaires = models.TextField(
        blank=True,
        verbose_name="Instructions supplémentaires",
        help_text="Instructions particulières pour ce médicament"
    )
    
    quantite_totale = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Quantité totale à délivrer",
        help_text="Nombre total d'unités à délivrer au patient"
    )
    
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Prescription de médicament"
        verbose_name_plural = "Prescriptions de médicaments"
        ordering = ['-date_created']
    
    def __str__(self):
        return f"{self.medicament.short_label} - {self.dose} {self.frequence}"
    
    def get_moment_display(self):
        """Retourne l'affichage du moment de prise"""
        if self.moment:
            return dict(self.MOMENT_CHOICES).get(self.moment, self.moment)
        return "Non spécifié"
    
    def get_frequence_display(self):
        """Retourne l'affichage de la fréquence"""
        return dict(self.FREQUENCE_CHOICES).get(self.frequence, self.frequence)
    
    def get_prescription_summary(self):
        """Retourne un résumé complet de la prescription"""
        summary = f"{self.medicament.short_label}\n"
        summary += f"Dose: {self.dose}\n"
        summary += f"Fréquence: {self.get_frequence_display()}\n"
        summary += f"Durée: {self.duree}\n"
        if self.moment:
            summary += f"Moment: {self.get_moment_display()}\n"
        if self.instructions_supplementaires:
            summary += f"Instructions: {self.instructions_supplementaires}\n"
        return summary
    
    @property
    def total_cost(self):
        """Calcule le coût total de cette prescription"""
        if self.quantite_totale and self.medicament.unit_price:
            return self.medicament.unit_price * self.quantite_totale
        return 0