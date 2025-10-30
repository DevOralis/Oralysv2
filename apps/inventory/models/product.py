from django.db import models
from .category import Category
from .unit_of_mesure import UnitOfMesure
from django.db.models import Sum
from apps.hr.models import Department 

class Product(models.Model): 
    _name = 'inventory.product'
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    default_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    barcode = models.CharField(max_length=50, unique=True, blank=True, null=True)
    standard_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    image_1920 = models.ImageField(upload_to='inventory_img/', blank=True, null=True)
    weight = models.FloatField(default=0)
    volume = models.FloatField(default=0)
    dlc = models.DateField(blank=True, null=True)
    stock_minimal = models.IntegerField(default=0)
    categ = models.ForeignKey(Category, on_delete=models.PROTECT, db_column='categ_id',blank=True, null=True)
    uom = models.ForeignKey(UnitOfMesure, on_delete=models.PROTECT, db_column='uom_id',blank=True, null=True)
    product_type = models.ForeignKey('ProductType', on_delete=models.PROTECT, db_column='product_type_id', null=True, blank=True)
    total_quantity_cached = models.DecimalField(max_digits=12, decimal_places=2, default=0)


    locations = models.ManyToManyField(
        'inventory.StockLocation',
        through='inventory.ProductLocation',
        related_name='products'
    )
    departments = models.ManyToManyField(
        Department,
        through='InventoryProductDepartment',
        related_name='inventory_products',
        blank=True
    )
    class Meta:
        db_table = 'inventory_product'

    def __str__(self):
        return self.name

    @property
    def total_quantity(self):
        """
        Dynamic sum of quantities in stock (all locations)
        """
        return (self.product_locations.aggregate(total=Sum('quantity_stored')).get('total') or 0)