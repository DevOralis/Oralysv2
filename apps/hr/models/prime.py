from django.db import models

class Prime(models.Model):
    libelle = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, help_text="Taux en pourcentage")
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Montant de la prime")

    def __str__(self):
        return self.libelle 