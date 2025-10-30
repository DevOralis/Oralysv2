from django.db import models

class ContractType(models.Model):
    """
    Model representing different types of employment contracts
    """
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        String representation of the ContractType model
        Returns: contract type name
        """
        return self.name

    class Meta:
        ordering = ['name']
