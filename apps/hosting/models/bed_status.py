from django.db import models


class BedStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    TRANSLATIONS = {
        "available": "Disponible",
        "occupied": "Occupé",
        "reserved": "Réservé",
        "maintenance": "Maintenance",
    }
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Statut de lit"
        verbose_name_plural = "Statuts de lit"