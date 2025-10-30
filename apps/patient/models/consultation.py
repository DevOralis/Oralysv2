from django.db import models
from apps.hr.models.employee import Employee
from apps.hr.models.speciality import Speciality
from .patient import Patient

class Consultation(models.Model):
    DEMANDE_CHOICES = [
        ('consultation_normale', 'Consultation normale'),
        ('hospitalisation', 'Hospitalisation'),
    ]
    
    TYPE_ADMISSION_CHOICES = [
        ('immediate', 'Admission immédiate (urgence)'),
        ('programmee', 'Admission programmée (planifié)'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consultations')
    medecin = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='consultations')
    speciality = models.ForeignKey(Speciality, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField("Date de la consultation", auto_now_add=True)
    commentaires = models.TextField("Commentaires", blank=True)
    traitement = models.TextField("Traitement", blank=True, help_text="Instructions de traitement générales")
    # Les médicaments sont maintenant gérés via MedicationPrescription
    # medicaments = models.ManyToManyField('pharmacy.PharmacyProduct', blank=True, verbose_name="Médicaments prescrits")
    temperature = models.DecimalField("Température (°C)", max_digits=4, decimal_places=1, null=True, blank=True)
    pression = models.CharField("Pression artérielle", max_length=20, blank=True)
    rythme_cardiaque = models.PositiveIntegerField("Rythme cardiaque (bpm)", null=True, blank=True)
    hospitalisation = models.BooleanField("Hospitalisation", default=False)
    demande_patient = models.CharField("Demande de patient", max_length=20, choices=DEMANDE_CHOICES, default='consultation_normale')
    type_admission = models.CharField("Type d'admission", max_length=20, choices=TYPE_ADMISSION_CHOICES, blank=True, null=True)
    date_admission_programmee = models.DateField("Date d'admission programmée", blank=True, null=True)
    consigne_alimentaire = models.TextField("Consigne alimentaire", blank=True, help_text="Instructions alimentaires spécifiques")
    consigne_hebergement = models.TextField("Consigne d'hébergement", blank=True, help_text="Instructions pour l'hébergement du patient")
    actes = models.ManyToManyField('patient.ActeTherapeutique', blank=True, verbose_name="Actes réalisés")
    is_invoiced = models.BooleanField("Facturée", default=False)
    
    def get_total_cost(self):
        """Calcule le coût total des actes de la consultation"""
        return sum(acte.price for acte in self.actes.all())
    
    def __str__(self):
        return f"Consultation de {self.patient} par {self.medecin} le {self.date:%d/%m/%Y}"
