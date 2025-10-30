from django.db import models

class SocialContribution(models.Model):
    label = models.CharField(max_length=255)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    ceiling = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.label} ({self.rate}%)" 