from django.db import models

class LocationType(models.Model):
    _name = 'inventory.locationType'
    location_type_id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'inventory_locationType'

    def __str__(self):
        return self.label