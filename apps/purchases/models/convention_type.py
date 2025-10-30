from django.db import models

class ConventionType(models.Model):
    libelle = models.CharField(max_length=255)
    class Meta:
        db_table = 'purchases_convention_types'

    def __str__(self):
        return self.libelle
