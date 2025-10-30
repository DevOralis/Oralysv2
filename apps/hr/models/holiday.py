from django.db import models


class Holiday(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()

    class Meta:
        ordering = ['date']
        unique_together = ('date', 'name')

    def __str__(self) -> str:
        return f"{self.name} ({self.date})"


