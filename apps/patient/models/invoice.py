from django.db import models
from django.conf import settings
from .patient import Patient
from .consultation import Consultation

class Invoice(models.Model):
    """Modèle pour les factures patient (consultations + hébergement)"""
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('sent', 'Envoyée'),
        ('paid', 'Payée'),
        ('overdue', 'En retard'),
    ]
    
    # Informations facture
    invoice_number = models.CharField("N° Facture", max_length=50, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='invoices')
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name='invoice', null=True, blank=True)
    
    # Dates
    created_date = models.DateTimeField("Date création", auto_now_add=True)
    invoice_date = models.DateField("Date facture", auto_now_add=True)
    due_date = models.DateField("Date échéance", blank=True, null=True)
    
    # Status et montants
    status = models.CharField("Statut", max_length=10, choices=STATUS_CHOICES, default='draft')
    total_amount = models.DecimalField("Montant total", max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField("Montant payé", max_digits=10, decimal_places=2, default=0)
    
    # Notes
    notes = models.TextField("Notes", blank=True)
    
    class Meta:
        ordering = ['-created_date']
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate invoice number
            import datetime
            today = datetime.date.today()
            count = Invoice.objects.filter(created_date__date=today).count() + 1
            self.invoice_number = f"FAC{today.strftime('%Y%m%d')}{count:03d}"
        
        # Le montant total est maintenant calculé dans les vues pour inclure hébergement
        super().save(*args, **kwargs)
    
    def get_consultations(self):
        """Récupérer toutes les consultations facturées liées à cette facture"""
        if self.consultation:
            # Si facture liée à une consultation spécifique, récupérer toutes les consultations facturées du patient à cette date
            return Consultation.objects.filter(
                patient=self.patient,
                is_invoiced=True,
                date__date=self.created_date.date()
            )
        return Consultation.objects.none()
    
    def get_admissions(self):
        """Récupérer toutes les admissions facturées liées à cette facture"""
        from apps.hosting.models import Admission
        return Admission.objects.filter(
            patient=self.patient,
            is_invoiced=True,
            admission_date__date=self.created_date.date()
        )
    
    @property
    def remaining_amount(self):
        return self.total_amount - self.paid_amount
    
    def __str__(self):
        return f"Facture {self.invoice_number} - {self.patient}"

