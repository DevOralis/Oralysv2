from django.db import models

class Department(models.Model):
    """
    Model representing company departments with hierarchical structure
    """
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        """
        String representation of the Department model
        Returns: department name with parent name if exists
        """
        if self.parent:
            return f"{self.name} ({self.parent.name})"
        return self.name
    
    def get_full_path(self):
        """Retourne le chemin complet du département (incluant tous les parents)"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name

    class Meta:
        ordering = ['name']
