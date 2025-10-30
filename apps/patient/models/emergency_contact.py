from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class EmergencyContact(models.Model):
    name         = models.CharField("Nom", max_length=100)
    phone        = PhoneNumberField("Téléphone", blank=True)
    relationship = models.CharField("Lien", max_length=50, blank=True)

    def __str__(self):
        return f"{self.name} ({self.relationship})"

