from django.db import models
import os
from django.utils import timezone
from apps.purchases.models.country import Country
from apps.purchases.models.city import City
from apps.purchases.models.language import Language

def supplier_logo_path(instance, filename):
    name = instance.name.replace(" ", "_").replace(":", "_").replace("/", "_")
    ext = filename.split('.')[-1]
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join('supplier_logos', f"{name}_{timestamp}.{ext}")

class PharmacySupplier(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    is_company = models.BooleanField(default=True)
    street = models.CharField(max_length=255, blank=True)
    street2 = models.CharField(max_length=255, blank=True)
    zip = models.CharField(max_length=20, blank=True)

    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pharmacy_suppliers_by_city'
    )

    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pharmacy_suppliers_by_country'
    )

    lang = models.ForeignKey(
        Language,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pharmacy_suppliers_by_language'
    )

    email = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    ICE = models.CharField(max_length=50, blank=True)
    RC = models.IntegerField(blank=True, null=True)
    IF = models.IntegerField(blank=True, null=True)
    vat = models.CharField(max_length=50, blank=True)
    RIB = models.CharField(max_length=100, blank=True)
    comment = models.TextField(blank=True)
    logo = models.ImageField(upload_to=supplier_logo_path, blank=True, null=True)

    class Meta:
        db_table = 'pharmacy_supplier'

    def __str__(self):
        return self.name
