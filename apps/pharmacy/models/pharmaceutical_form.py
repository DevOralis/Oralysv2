# apps/pharmacy/models/pharmaceutical_form.py

from django.db import models

class PharmaceuticalForm(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'pharmacy_pharmaceutical_form'
       

    def __str__(self):
        return self.name
