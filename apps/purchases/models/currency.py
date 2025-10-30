# models/currency.py
from django.db import models

class Currency(models.Model):
    libelle = models.CharField(max_length=50)  # Exemple : "Euro", "Dollar"
    abreviation = models.CharField(max_length=10)  # Exemple : "EUR", "USD"

    class Meta:
        db_table = 'purchases_currency'

    def __str__(self):
        return f"{self.abreviation} - {self.libelle}"
