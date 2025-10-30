from django.db import models
from .product import Product
from .stock_location import StockLocation

class ProductLocation(models.Model):
    product_location_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_locations')
    location = models.ForeignKey(
        StockLocation,
        on_delete=models.CASCADE,
        related_name='product_locations',
        db_column='location_id'
    )

    quantity_stored = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text="Physical quantity currently on hand"
    )
    last_count_date = models.DateField(
        null=True, blank=True,
        help_text="Date of the last stock count"
    )
    quantity_counted = models.DecimalField(max_digits=12, decimal_places=2, default=0,null=True, blank=True,help_text="Physical quantity counted during inventory")


    class Meta:
        db_table = 'inventory_product_location'
        unique_together = ('product', 'location')
        verbose_name = 'Product / Location'
        verbose_name_plural = 'Products / Locations'

    def __str__(self):
        return f'{self.product} @ {self.location} (qty={self.quantity_stored})'