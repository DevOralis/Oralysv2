from django.db import models
from apps.hr.models import Department

class InventoryProductDepartment(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='product_departments')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='department_products')
    quantity_stored = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'inventory_product_department'
        unique_together = ('product', 'department')  

    def __str__(self):
        return f"{self.product.name} - {self.department.name} : {self.quantity_stored}"