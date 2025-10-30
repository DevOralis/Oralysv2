from django.db import models
from .contract_type import ContractType

class Contract(models.Model):
    """
    Model representing an employee's contract
    """
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='contracts')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    contract_type = models.ForeignKey(ContractType, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        String representation of the Contract model
        Returns: contract type and dates
        """
        end_date_str = f" - {self.end_date}" if self.end_date else " - En cours"
        return f"{self.employee.full_name} - {self.contract_type} ({self.start_date}{end_date_str})"

    class Meta:
        ordering = ['-start_date']
