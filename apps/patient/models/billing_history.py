from django.db import models
from django.conf import settings

class BillingHistory(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('pending', 'En attente'),
        ('paid', 'Payée'),
        ('overdue', 'En retard'),
    ]
    
    invoice_number = models.CharField("N° Facture", max_length=50, unique=True, blank=True, null=True)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='billing_history')
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    billing_date = models.DateField()
    due_date = models.DateField("Date échéance", blank=True, null=True)
    status = models.CharField("Statut", max_length=10, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Historique de Facturation"
        verbose_name_plural = "Historiques de Facturation"
        ordering = ['-generated_at']
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Générer un numéro de facture unique
            import datetime
            today = datetime.date.today()
            # Compter les factures du jour
            count = BillingHistory.objects.filter(generated_at__date=today).count() + 1
            self.invoice_number = f"FAC{today.strftime('%Y%m%d')}{count:03d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Facture {self.invoice_number} - {self.patient} - {self.total_amount} DH ({self.generated_at.strftime('%d/%m/%Y')})"
