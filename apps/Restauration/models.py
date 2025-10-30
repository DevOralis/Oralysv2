from django.db import models
from django.db import connection
from datetime import date
from apps.patient.models import Patient

class Plat(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

class Recette(models.Model):
    plat = models.OneToOneField(Plat, on_delete=models.CASCADE, related_name='recette')

    def __str__(self):
        return f"Recette pour {self.plat.nom}"

class IngredientCategorie(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

class Ingredient(models.Model):
    nom = models.CharField(max_length=100)
    unite = models.CharField(max_length=20)
    categorie = models.ForeignKey(IngredientCategorie, on_delete=models.CASCADE, related_name='ingredients', null=True, blank=True)

    def __str__(self):
        return f"{self.nom} ({self.unite})"

class LigneRecette(models.Model):
    recette = models.ForeignKey(Recette, on_delete=models.CASCADE, related_name='lignes_recette')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantite_par_portion = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantite_par_portion} {self.ingredient.unite} de {self.ingredient.nom} pour {self.recette.plat.nom}"

class MenuStandard(models.Model):
    date = models.DateField(null=True, blank=True, default=date.today)
    REPAS_CHOICES = [
        ('Petit déjeuner', 'Petit déjeuner (07h00)'),
        ('Déjeuner', 'Déjeuner (12h30)'),
        ('Collation', 'Collation (16h30)'),
        ('Dîner', 'Dîner (20h00)'),
    ]
    repas = models.CharField(max_length=20, choices=REPAS_CHOICES, default='Petit déjeuner')
    plats = models.ManyToManyField(Plat)

class Programme(models.Model):
    nom = models.CharField(max_length=100)
    date_debut = models.DateField()
    date_fin = models.DateField()
    lieu = models.CharField(max_length=100)
    population = models.CharField(max_length=50, default='patients')

    def __str__(self):
        return self.nom

class ProgrammeJour(models.Model):
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name='jours')
    date = models.DateField()
    menu = models.ForeignKey(MenuStandard, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ('programme', 'date')
        ordering = ['date']

    def __str__(self):
        return f"{self.programme.nom} - {self.date}"

class ProgrammeJourMenu(models.Model):
    """Modèle pour gérer les menus spécifiques à chaque jour de programme"""
    programme_jour = models.OneToOneField(ProgrammeJour, on_delete=models.CASCADE, related_name='menu_personnalise')
    plats = models.ManyToManyField(Plat, verbose_name="Plats sélectionnés")
    heure_service = models.TimeField(verbose_name="Heure de service", help_text="Heure à laquelle le menu sera servi")
    description = models.TextField(blank=True, verbose_name="Description/Remarques", help_text="Notes spéciales pour ce menu")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Menu du jour de programme"
        verbose_name_plural = "Menus des jours de programme"

    def __str__(self):
        return f"Menu du {self.programme_jour.date} - {self.programme_jour.programme.nom}"

class MenuPersonnalise(models.Model):
    client = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Client")
    num_chambre = models.CharField(max_length=10, null=True, blank=True)
    date = models.DateField(null=True, blank=True, default=date.today)
    repas = models.CharField(max_length=50, choices=MenuStandard.REPAS_CHOICES, default='Petit déjeuner')
    quantite = models.PositiveIntegerField(default=1)
    plats = models.ManyToManyField(Plat)
    description = models.TextField(blank=True, help_text="Description ou remarques spéciales")

    def __str__(self):
        client_name = str(self.client) if self.client else "Client non spécifié"
        return f"{client_name} - Chambre {self.num_chambre} ({self.date})"

class MenuSupplementaire(models.Model):
    client = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Client")
    num_chambre = models.CharField(max_length=10, null=True, blank=True)
    date = models.DateField(null=True, blank=True, default=date.today)
    repas = models.CharField(max_length=20, choices=MenuStandard.REPAS_CHOICES, default='Petit déjeuner')
    quantite = models.PositiveIntegerField(default=1)

    def __str__(self):
        client_name = str(self.client) if self.client else "Client non spécifié"
        return f"{client_name} - Chambre {self.num_chambre} ({self.date})"

