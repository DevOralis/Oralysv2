from django.db import models

class Position(models.Model):
    """
    Model representing job positions in the company
    """
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        String representation of the Position model
        Returns: position name
        """
        return self.name

    class Meta:
        ordering = ['name']
