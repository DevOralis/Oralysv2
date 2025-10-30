# apps/home/models/employee.py
from django.db import models
from .position import Position
from .department import Department
from .contract import Contract
from .child import Child
from .model_calcul import ModelCalcul
from .speciality import Speciality

class Employee(models.Model):
    # Enumerations
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('S', 'Single'),
        ('M', 'Married'),
        ('D', 'Divorced'),
        ('W', 'Widowed'),
    ]

    STATUS_CHOICES = [
        ('A', 'Active'),
        ('I', 'Inactive'),
    ]

    YES_NO_CHOICES = [
        (0, 'No'),
        (1, 'Yes'),
    ]

    # Basic fields
    employee_id = models.CharField(max_length=50, unique=True)
    national_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=255)
    birth_date = models.DateField()
    photo = models.ImageField(upload_to='hr_media/employees_profile/', null=True, blank=True)
    marital_status = models.CharField(max_length=1, choices=MARITAL_STATUS_CHOICES)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    email = models.EmailField()
    personal_phone = models.CharField(max_length=20)
    work_phone = models.CharField(max_length=20)

    # Addresses
    personal_address = models.TextField(null=True, blank=True)
    work_address = models.TextField(null=True, blank=True)

    # Family & children
    children_count = models.PositiveIntegerField(default=0)
    children = models.ManyToManyField(Child, blank=True, related_name='parents')

    # Status & employment
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    # contract relation is now handled via Contract.employee (reverse relation: employee.contracts)
    speciality = models.ForeignKey(Speciality, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Spécialité")

    # Attachments
    work_certificate = models.FileField(upload_to='hr_media/certificates/', null=True, blank=True)
    legalized_contract = models.FileField(upload_to='hr_media/legalized_contracts/', null=True, blank=True)
    doctor_agreement = models.FileField(upload_to='hr_media/doctor_agreements/', null=True, blank=True)
    temporary_agreement = models.FileField(upload_to='hr_media/temporary_agreements/', null=True, blank=True)

    # Salary
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    model_calcul = models.ForeignKey(ModelCalcul, null=True, blank=True, on_delete=models.SET_NULL)

    # Career
    career_evolution = models.TextField(null=True, blank=True)
    skills = models.TextField(null=True, blank=True)

    # Reflexive association
    is_supervisor = models.IntegerField(choices=YES_NO_CHOICES, default=0)
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')

    def __str__(self):
        return f"{self.full_name} - {self.employee_id}"