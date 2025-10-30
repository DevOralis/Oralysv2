from django.db import models

class OperationType(models.Model):
    _name = 'inventory.operationType'
    operation_type_id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=100, unique=True)
    class Meta:
        db_table = 'inventory_operationType'

    def __str__(self):
        return self.label 