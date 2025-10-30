from django.db import models
from django.conf import settings
from .billing_history import BillingHistory

class Payment(models.Model):
    PAYMENT_CHANNEL_CHOICES = [
        ('cash', 'Espèces'),
        ('check', 'Chèque'),
        ('transfer', 'Virement'),
        ('card', 'Carte bancaire'),
        ('mobile', 'Mobile money'),
    ]
    
    PAYMENT_MODE_CHOICES = [
        ('full', 'Paiement total'),
        ('partial', 'Paiement partiel'),
        ('advance', 'Acompte'),
    ]
    
    billing_history = models.ForeignKey(BillingHistory, on_delete=models.CASCADE, related_name='payments')
    journal = models.CharField("Journal", max_length=100, blank=True)
    payment_channel = models.CharField("Canal de paiement", max_length=20, choices=PAYMENT_CHANNEL_CHOICES, default='cash')
    payment_mode = models.CharField("Mode de paiement", max_length=20, choices=PAYMENT_MODE_CHOICES, default='full')
    beneficiary_account = models.CharField("Compte bancaire du bénéficiaire", max_length=100, blank=True)
    amount = models.DecimalField("Montant", max_digits=10, decimal_places=2)
    payment_date = models.DateField("Date de règlement")
    memo = models.CharField("Mémo", max_length=200, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Paiement {self.amount} DH - {self.billing_history.invoice_number} ({self.payment_date})"



