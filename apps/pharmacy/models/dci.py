from django.db import models

class Dci(models.Model):
    _name = 'pharmacy.dci'
    dci_id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=255, unique=True, verbose_name='Nom DCI')
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'pharmacy_dci'

    def __str__(self):
        return self.label