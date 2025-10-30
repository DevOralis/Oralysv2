from django.db import models

class Acte(models.Model):
    libelle = models.CharField(max_length=255, verbose_name="Libellé")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix")

    def __str__(self):
        return self.libelle

    class Meta:
        verbose_name = "Acte"
        verbose_name_plural = "Actes"
