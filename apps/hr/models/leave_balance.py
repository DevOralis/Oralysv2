from django.db import models
from django.core.validators import MinValueValidator
from .employee import Employee
from .leave_type import LeaveType

class LeaveBalance(models.Model):
    balance_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_balances'
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name='balances'
    )
    year = models.IntegerField()
    entitlement = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0
    )
    taken = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0
    )
    remaining = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        unique_together = ('employee', 'leave_type', 'year')
        db_table = 'hr_leave_balance'

    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} ({self.year})"

    def save(self, *args, **kwargs):
        # Calculer automatiquement le solde restant
        # Gérer le cas où entitlement ou taken peuvent être None
        entitlement = self.entitlement or 0
        taken = self.taken or 0
        self.remaining = entitlement - taken
        super().save(*args, **kwargs) 