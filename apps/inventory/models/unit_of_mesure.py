from django.db import models

class UnitOfMesure(models.Model):
    _name = 'inventory.unitofmesure'
    uom_id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=50, unique=True)
    symbole = models.CharField(max_length=10)

    class Meta:
        db_table = 'inventory_unitofmesure'

    def __str__(self):
        return f"{self.label} ({self.symbole})"