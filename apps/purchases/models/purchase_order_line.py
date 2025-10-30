from django.db import models
from .purchase_order import PurchaseOrder
from apps.inventory.models.product import Product
from apps.inventory.models.unit_of_mesure import UnitOfMesure
from .taxes import Tax

class PurchaseOrderLine(models.Model):
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='order_lines')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_qty = models.FloatField()
    product_uom = models.ForeignKey(UnitOfMesure, on_delete=models.PROTECT, null=True, blank=True)
    price_unit = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.ForeignKey(Tax, on_delete=models.PROTECT, null=True, blank=True)  # Changé en ForeignKey
    price_subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    name = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'purchases_order_line'

    def __str__(self):
        return f"{self.product.name} x {self.product_qty}"