from django.db import models
from django.core.validators import MinValueValidator

class LeaveType(models.Model):
    """
    Modèle pour les types de congés
    """
    ACCRUAL_CHOICES = [
        ('annual', 'Annuel'),
        ('monthly', 'Mensuel'),
    ]
    
    type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name="Nom")
    default_days = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True,
        blank=True,
        validators=[MinValueValidator(0)], 
        verbose_name="Jours par défaut",
        help_text="Nombre de jours attribués par défaut (optionnel)"
    )
    accrual_method = models.CharField(
        max_length=10, 
        choices=ACCRUAL_CHOICES, 
        default='annual', 
        verbose_name="Méthode d'acquisition",
        help_text="Comment les jours de congé sont accumulés"
    )
    year = models.IntegerField(
        null=True, 
        blank=True, 
        verbose_name="Année",
        help_text="Année pour laquelle ce type de congé est applicable"
    )
    active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si ce type de congé est actuellement actif"
    )
    
    # Jours de travail
    monday = models.BooleanField(default=True, verbose_name="Lundi")
    tuesday = models.BooleanField(default=True, verbose_name="Mardi")
    wednesday = models.BooleanField(default=True, verbose_name="Mercredi")
    thursday = models.BooleanField(default=True, verbose_name="Jeudi")
    friday = models.BooleanField(default=True, verbose_name="Vendredi")
    saturday = models.BooleanField(default=False, verbose_name="Samedi")
    sunday = models.BooleanField(default=False, verbose_name="Dimanche")
    
    description = models.TextField(null=True, blank=True, verbose_name="Description")

    class Meta:
        verbose_name = "Type de congé"
        verbose_name_plural = "Types de congés"
        ordering = ['name']

    def __str__(self):
        year_str = f" ({self.year})" if self.year else ""
        return f"{self.name}{year_str}"
        
    def is_working_day(self, weekday):
        """
        Vérifie si un jour est un jour de travail selon la configuration
        weekday: 0 = Lundi, 1 = Mardi, ..., 6 = Dimanche
        """
        working_days = {
            0: self.monday,
            1: self.tuesday,
            2: self.wednesday,
            3: self.thursday,
            4: self.friday,
            5: self.saturday,
            6: self.sunday
        }
        return working_days.get(weekday, False) 