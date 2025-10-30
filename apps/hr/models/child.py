from django.db import models

class Child(models.Model):
    """
    Model representing an employee's child
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birth_date = models.DateField(null=True, blank=True)
    is_scolarise = models.BooleanField(default=False, verbose_name="Scolarisé")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        String representation of the Child model
        Returns: child's name and gender
        """
        return f"{self.name} ({self.get_gender_display()})"

    class Meta:
        ordering = ['name']
