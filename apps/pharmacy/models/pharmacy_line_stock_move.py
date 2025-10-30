from django.db import models
from .pharmacy_product_uom import PharmacyUnitOfMesure
from .pharmacy_stock_move import PharmacyStockMove
from .product import PharmacyProduct

class PharmacyLineStockMove(models.Model):
    line_id = models.AutoField(primary_key=True)
    move = models.ForeignKey(
        PharmacyStockMove, on_delete=models.CASCADE, related_name='lines'
    )
    product = models.ForeignKey(
        PharmacyProduct, on_delete=models.PROTECT, related_name='pharmacy_move_lines'
    )
    quantity_demanded = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity_arrived = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, default=0)
    uom = models.ForeignKey(PharmacyUnitOfMesure, on_delete=models.PROTECT)

    class Meta:
        db_table = 'pharmacy_line_stock_move'
        verbose_name = 'Ligne de mouvement pharmacie'
        verbose_name_plural = 'Lignes de mouvement pharmacie'

    def __str__(self):
        return f"{self.product.short_label} – {self.quantity_demanded} {self.uom}"
