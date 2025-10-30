from django.db import models
from .pharmacy_order import PharmacyOrder
from .product import PharmacyProduct
from apps.purchases.models.taxes import Tax
from apps.inventory.models.unit_of_mesure import UnitOfMesure
from decimal import Decimal

class PharmacyOrderLine(models.Model):
    order = models.ForeignKey('PharmacyOrder', related_name='order_lines', on_delete=models.CASCADE)
    product = models.ForeignKey('PharmacyProduct', on_delete=models.CASCADE, blank=True, null=True)
    product_qty = models.FloatField(blank=True, null=True)
    price_unit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True, blank=True)
    price_subtotal = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True)
    def save(self, *args, **kwargs):
        if self.product_qty is not None and self.price_unit is not None:
            self.price_subtotal = Decimal(str(self.product_qty)) * self.price_unit
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'pharmacy_order_line'

    def __str__(self):
        return f"{self.product} x {self.product_qty}"