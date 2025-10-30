from django.db import models

class ProductType(models.Model):
    _name = 'inventory.productType'
    product_type_id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=100, unique=True)
    class Meta:
        db_table = 'inventory_productType'

    def __str__(self):
        return self.label