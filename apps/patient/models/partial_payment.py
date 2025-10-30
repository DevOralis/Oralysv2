from django.db import models
from .payment import Payment


class PartialPayment(models.Model):
    """Modèle pour les versements d'un paiement partiel"""
    
    PAYMENT_CHANNEL_CHOICES = [
        ('cash', 'Espèces'),
        ('check', 'Chèque'),
    ]
    
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='partial_payments',
        verbose_name="Paiement"
    )
    payment_number = models.IntegerField("N° du versement", help_text="1er, 2e, 3e...")
    payment_channel = models.CharField(
        "Canal de paiement",
        max_length=20,
        choices=PAYMENT_CHANNEL_CHOICES,
        default='cash'
    )
    amount = models.DecimalField("Montant", max_digits=10, decimal_places=2)
    payment_date = models.DateField("Date de paiement")
    due_date = models.DateField("Date d'échéance")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Versement partiel"
        verbose_name_plural = "Versements partiels"
        ordering = ['payment_number']
    
    def __str__(self):
        return f"Versement {self.payment_number} - {self.amount} DH ({self.get_payment_channel_display()})"


