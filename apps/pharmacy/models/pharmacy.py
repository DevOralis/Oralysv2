from django.db import models

class Pharmacy(models.Model):
    pharmacy_id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=255, unique=True, verbose_name='Nom de la pharmacie')
    adress = models.TextField(blank=True)

    class Meta:
        db_table = 'pharmacy_pharmacy'

    def __str__(self):
        return self.label