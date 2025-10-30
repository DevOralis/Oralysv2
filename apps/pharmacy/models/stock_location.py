from django.db import models
from .pharmacy import Pharmacy

class PharmacyStockLocation(models.Model):
    location_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    parent_location = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children', db_column='parent_location_id'
    )
    location_type = models.ForeignKey(
        'PharmacyLocationType', on_delete=models.PROTECT, db_column='location_type_id'
    )
    pharmacy = models.ForeignKey(
            'Pharmacy', on_delete=models.CASCADE,
            db_column='pharmacy_id',
            verbose_name="Pharmacie associée",
            null=True, blank=True 
      )

    class Meta:
        db_table = 'pharmacy_stockLocation'

    def __str__(self):
        return self.name