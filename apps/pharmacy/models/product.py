from django.db import models
from .dci import Dci
from .pharmaceutical_form import PharmaceuticalForm
from .stock_location import PharmacyStockLocation
from .pharmacy_product_uom import PharmacyUnitOfMesure
from .pharmacy_product_category import PharmacyProductCategory
from apps.hr.models import Department 
from django.db.models import Sum

class PharmacyProduct(models.Model):
    product_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    short_label = models.CharField(max_length=100, verbose_name="Libellé court")
    brand = models.CharField(max_length=100, blank=True, null=True)
    full_label = models.CharField(max_length=255, blank=True, null=True)
    dci = models.ForeignKey(Dci, on_delete=models.PROTECT, db_column='dci_id', blank=True, null=True)
    pharmaceutical_form = models.ForeignKey(PharmaceuticalForm, on_delete=models.PROTECT, db_column='pharmaceutical_form_id', blank=True, null=True)
    dosage = models.CharField(max_length=50, blank=True, null=True)
    barcode = models.CharField(max_length=30, unique=True, blank=True, null=True)
    ppm_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supplier_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    internal_purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    uom = models.ForeignKey(PharmacyUnitOfMesure, on_delete=models.PROTECT, db_column='uom_id', blank=True, null=True)
    categ = models.ForeignKey(PharmacyProductCategory, on_delete=models.PROTECT, db_column='categ_id', blank=True, null=True)
    total_quantity_cached = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    nombrepiece = models.PositiveIntegerField(blank=True, null=True, verbose_name="Nombre de pièces par boîte")

    locations = models.ManyToManyField(
        PharmacyStockLocation,
        through='PharmacyProductLocation',
        related_name='products'
    )
    departments = models.ManyToManyField(
        Department,
        through='PharmacyProductDepartment',
        related_name='pharmacy_products',
        blank=True
    )

    class Meta:
        db_table = 'pharmacy_product'

    def __str__(self):
        return f"{self.code} - {self.short_label}"

    @property
    def total_quantity(self):
        return (self.pharmacy_product_locations.aggregate(total=Sum('quantity_stored')).get('total') or 0)