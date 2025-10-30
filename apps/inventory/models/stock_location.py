from django.db import models

class StockLocation(models.Model):
    _name = 'inventory.stockLocation'
    location_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    parent_location = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children', db_column='parent_location_id'
        )
    location_type = models.ForeignKey(
        'LocationType', on_delete=models.PROTECT, db_column='location_type_id'
        )

    class Meta:
        db_table = 'inventory_stockLocation'

    def __str__(self):
        return self.name 