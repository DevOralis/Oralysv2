from django.db import models
from .convention import Convention
from apps.inventory.models.product import Product
from apps.inventory.models.unit_of_mesure import UnitOfMesure
from apps.purchases.models.taxes import Tax

class ConventionLine(models.Model):
    convention = models.ForeignKey(Convention, on_delete=models.CASCADE, related_name='convention_lines')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_qty = models.FloatField()
    price_unit = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.ForeignKey(Tax, on_delete=models.PROTECT, null=True, blank=True)
    price_subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    name = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'purchases_convention_lines'

    def __str__(self):
        return f"{self.product.name} x {self.product_qty}"
