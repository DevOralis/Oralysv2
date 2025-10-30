from django.db import models
from django.utils import timezone
from .supplier import PharmacySupplier 
from .product import PharmacyProduct
from apps.purchases.models.currency import Currency
from apps.purchases.models.taxes import Tax
from apps.purchases.models.payment_mode import PaymentMode

class PharmacyOrder(models.Model):
    STATE_CHOICES = [
        ('draft', 'Brouillon'),
        ('waiting', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('partial', 'Réception partielle'),
        ('done', 'Fermé'),
    ]

    INVOICE_STATUS_CHOICES = [
        ('to_invoice', 'À facturer'),
        ('partial', 'Partiellement facturé'),
        ('invoiced', 'Totalement facturé'),
    ]

    name = models.CharField(max_length=100, unique=True)
    supplier = models.ForeignKey(PharmacySupplier, on_delete=models.PROTECT, related_name='pharmacy_orders')
    date_order = models.DateField(default=timezone.now)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='draft')
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    amount_untaxed = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    invoice_status = models.CharField(max_length=20, choices=INVOICE_STATUS_CHOICES, default='to_invoice')
    date_planned = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    supplier_ref = models.CharField(max_length=100, blank=True, null=True)
    payment_mode = models.ForeignKey(PaymentMode, on_delete=models.SET_NULL, null=True, blank=True, related_name='pharmacy_orders')

    class Meta:
        db_table = 'pharmacy_order'

    def __str__(self):
        return self.name