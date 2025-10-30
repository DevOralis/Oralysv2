from django.db import models

class PharmacyLocationType(models.Model):
    location_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'pharmacy_locationType'

    def __str__(self):
        return self.name