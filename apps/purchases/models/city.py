from django.db import models
from .country import Country
class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    class Meta:
        db_table = 'purchases_city'

    def __str__(self):
        return self.name