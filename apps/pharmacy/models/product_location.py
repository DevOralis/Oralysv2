from django.db import models
from .product import PharmacyProduct
from .stock_location import PharmacyStockLocation

class PharmacyProductLocation(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(PharmacyProduct, on_delete=models.CASCADE, db_column='product_id', related_name='pharmacy_product_locations')
    location = models.ForeignKey(PharmacyStockLocation, on_delete=models.CASCADE, db_column='location_id', related_name='pharmacy_product_locations')
    quantity_stored = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity_counted = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_count_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'pharmacy_product_location'
        unique_together = ('product', 'location')

