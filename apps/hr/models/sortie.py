from django.db import models

class Sortie(models.Model):
    TYPE_SORTIE = [
        ('DEMISSION', 'Démission'),
        ('RETRAITE', 'Départ à la retraite'),
        ('LICENCIEMENT', 'Licenciement'),
    ]
    
    employe_nom = models.CharField(max_length=100)
    type_sortie = models.CharField(max_length=20, choices=TYPE_SORTIE)
    motif = models.TextField()
    date_sortie = models.DateField()
    fichier = models.FileField(upload_to='sorties/', blank=True, null=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employe_nom} - {self.get_type_sortie_display()}"

    class Meta:
        verbose_name = 'Sortie'
        verbose_name_plural = 'Sorties'
        ordering = ['-date_sortie']
