from django.db import models

class PharmacyOperationType(models.Model):
    operation_type_id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=100, unique=True)
    class Meta:
        db_table = 'pharmacy_operation_type'

    def __str__(self):
        return self.label 