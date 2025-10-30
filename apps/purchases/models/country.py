from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'purchases_country'

    def __str__(self):
        return self.name
