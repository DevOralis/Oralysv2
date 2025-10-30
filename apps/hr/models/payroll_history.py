from django.db import models
from .employee import Employee

class PayrollGenerationHistory(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payrolls_generated_for')
    generated_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='payrolls_generated_by')
    generated_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.employee} - {self.generated_at}" 