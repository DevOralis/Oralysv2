from django.db import models
from apps.hr.models import Department
from .product import PharmacyProduct

class PharmacyProductDepartment(models.Model):
    product = models.ForeignKey(PharmacyProduct, on_delete=models.CASCADE, related_name='pharmacy_product_departments')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='pharmacy_department_products')
    quantity_stored = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'pharmacy_product_department'
        unique_together = ('product', 'department')  

    def __str__(self):
        return f"{self.product.short_label} - {self.department.name} : {self.quantity_stored}"