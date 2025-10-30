from django.db import models

class PharmacyProductCategory(models.Model):
    categ_id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'pharmacy_product_category'

    def __str__(self):
        return self.label