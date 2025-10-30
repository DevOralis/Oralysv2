from django.db import models

class Language(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'purchases_language'

    def __str__(self):
        return self.name