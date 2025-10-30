from django.db import models
from .supplier import Supplier
from .convention_type import ConventionType
from .currency import Currency 

def convention_upload_path(instance, filename):
    return f"conventions/{instance.id}/{filename}"

class Convention(models.Model):
    STATE_CHOICES = [
        ('draft', 'Brouillon'),
        ('active', 'Active'),
        ('confirmed', 'Confirmée'),  # <-- ajouté ici
        ('expired', 'Expirée'),
        ('cancelled', 'Annulée'),
    ]



    name = models.CharField(max_length=100, unique=True)
    partner = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='conventions')
    convention_type = models.ForeignKey(ConventionType, on_delete=models.PROTECT, related_name='conventions')
    date_start = models.DateField()
    date_end = models.DateField()
    general_conditions = models.TextField()
    attachments = models.FileField(upload_to=convention_upload_path, null=True, blank=True)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='draft')
    amount_untaxed = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='conventions')


    class Meta:
        db_table = 'purchases_conventions'
        ordering = ['-date_start']

    def __str__(self):
        return self.name