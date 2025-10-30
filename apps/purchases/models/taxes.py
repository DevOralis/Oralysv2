from django.db import models

class Tax(models.Model):
    libelle = models.CharField(max_length=100)
    valeur = models.DecimalField(max_digits=5, decimal_places=2)  # pour stocker des pourcentages, ex: 20.00 pour 20%

    class Meta:
        db_table = 'purchases_tax'

    def __str__(self):
        return f"{self.libelle} ({self.valeur}%)"
