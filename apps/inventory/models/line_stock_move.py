from django.db import models
from .unit_of_mesure import UnitOfMesure
from .stock_move import StockMove
from .product import Product

class LineStockMove(models.Model):
    line_id = models.AutoField(primary_key=True)
    move = models.ForeignKey(
        StockMove,        
        on_delete=models.CASCADE,
        related_name='lines',
        db_column='move_id'
    )
    product = models.ForeignKey(
        Product,        
        on_delete=models.PROTECT,
        related_name='move_lines',
        db_column='product_id'
    )
    quantity_demanded = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity_arrived = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, default=0)
    uom = models.ForeignKey(
        UnitOfMesure,
        on_delete=models.PROTECT,
        db_column='uom_id'
    )

    class Meta:
        db_table = 'inventory_line_stock_move'
        verbose_name = 'Ligne de mouvement'
        verbose_name_plural = 'Lignes de mouvement'

    def __str__(self):
        return f"{self.product} – {self.quantity_demanded} {self.uom}"
