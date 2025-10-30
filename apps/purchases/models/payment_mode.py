from django.db import models

class PaymentMode(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'purchases_payment_mode'

    def __str__(self):
        return self.name
