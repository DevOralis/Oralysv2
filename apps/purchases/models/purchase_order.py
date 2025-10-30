from django.db import models
from .supplier import Supplier
from .currency import Currency
from .taxes import Tax
from .payment_mode import PaymentMode

class PurchaseOrder(models.Model):
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

    DELIVERY_STATUS_CHOICES = [
        ('complete', 'Complète'),
        ('partial', 'Partielle'),
    ]

    name = models.CharField(max_length=100, unique=True)
    partner = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders')
    date_order = models.DateField()
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='draft')
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    amount_untaxed = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    invoice_status = models.CharField(max_length=20, choices=INVOICE_STATUS_CHOICES, default='to_invoice')
    date_planned = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    supplier_ref = models.CharField(max_length=100, blank=True, null=True)  # nouveau champ
    payment_mode = models.ForeignKey(PaymentMode, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_orders')


    class Meta:
        db_table = 'purchases_order'

    def __str__(self):
        return self.name