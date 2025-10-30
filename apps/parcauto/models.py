from django.db import models
from django.utils import timezone
from datetime import date
from django.core.validators import MinValueValidator
from apps.hr.models import Employee

class TypeVehicule(models.TextChoices):
    UTILITAIRE = 'utilitaire', 'Utilitaire'
    TOURISME = 'tourisme', 'Tourisme'
    CAMION = 'camion', 'Camion'
    AUTRE = 'autre', 'Autre'

class StatutVehicule(models.TextChoices):
    DISPONIBLE = 'disponible', 'Disponible'
    EN_SERVICE = 'en_service', 'En service'
    MAINTENANCE = 'maintenance', 'En maintenance'

class Marque(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='parcauto/logo/', null=True, blank=True)

    def __str__(self):
        return self.nom

class Modele(models.Model):
    nom = models.CharField(max_length=100)
    marque = models.ForeignKey(Marque, on_delete=models.CASCADE, related_name='modeles')

    class Meta:
        unique_together = ('nom', 'marque')

    def __str__(self):
        return f"{self.nom} ({self.marque.nom})"

class Vehicule(models.Model):
    immatriculation = models.CharField(max_length=20, unique=True)
    marque = models.ForeignKey(Marque, on_delete=models.PROTECT)
    modele = models.ForeignKey(Modele, on_delete=models.PROTECT)
    annee = models.PositiveIntegerField()
    type = models.CharField(max_length=20, choices=TypeVehicule.choices)
    statut = models.CharField(max_length=20, choices=StatutVehicule.choices)
    image = models.ImageField(upload_to='parcauto/image/', null=True, blank=True)
    kilometrage_actuel = models.PositiveIntegerField()
    date_achat = models.DateField(default=timezone.now)
    date_mise_service = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.immatriculation} - {self.marque.nom} {self.modele.nom}"

class TypeEntretien(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom du type d'entretien")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Type d'entretien"
        verbose_name_plural = "Types d'entretien"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom

class StatutEntretien(models.TextChoices):
    PLANIFIE = 'planifié', 'Planifié'
    EFFECTUE = 'effectué', 'Effectué'
    EN_RETARD = 'en_retard', 'En retard'

class Entretien(models.Model):
    vehicle = models.ForeignKey('Vehicule', on_delete=models.CASCADE, related_name='entretiens')
    type_entretien = models.ForeignKey(TypeEntretien, on_delete=models.PROTECT, verbose_name="Type d'entretien", null=True)
    date_planifiee = models.DateField(verbose_name="Date planifiée")
    StatutEntretien = models.CharField(max_length=20, choices=StatutEntretien.choices, default=StatutEntretien.PLANIFIE)
    remarque = models.TextField(blank=True, null=True, verbose_name="Remarques")
    piece_jointe = models.FileField(
        upload_to='parcauto/pieces_jointes/', 
        blank=True, 
        null=True, 
        verbose_name="Pièce jointe"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Entretien"
        verbose_name_plural = "Entretiens"
        ordering = ['-date_planifiee']

    def __str__(self):
        return f"Entretien {self.id} - {self.vehicle.immatriculation} - {self.type_entretien.nom}"

class Affectation(models.Model):
    STATUS_CHOICES = [
        ('A', 'Active'),
        ('T', 'Terminée'),
    ]
    
    vehicle = models.ForeignKey('Vehicule', on_delete=models.CASCADE, related_name='assignments')
    driver = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='vehicle_assignments')
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    kilometrage_debut = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    kilometrage_fin = models.PositiveIntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    distance_parcourue = models.PositiveIntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    duree_jours = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'
        ordering = ['-date_debut']
        constraints = [
            models.UniqueConstraint(
                fields=['vehicle', 'driver'],
                condition=models.Q(statut='A'),
                name='unique_active_assignment'
            )
        ]

    def __str__(self):
        return f"{self.vehicle.immatriculation} → {self.driver.full_name}"

    def is_active(self):
        return self.statut == 'A'

    def calculate_stats(self):
        if self.kilometrage_fin is not None and self.kilometrage_debut is not None:
            try:
                self.distance_parcourue = int(self.kilometrage_fin) - int(self.kilometrage_debut)
            except (ValueError, TypeError):
                self.distance_parcourue = None
        
        if self.date_fin and self.date_debut:
            self.duree_jours = (self.date_fin - self.date_debut).days

    def save(self, *args, **kwargs):
        self.calculate_stats()
        
        if self.pk is None:
            self.vehicle.statut = StatutVehicule.EN_SERVICE
            self.vehicle.kilometrage_actuel = int(self.kilometrage_debut)
            self.vehicle.save()
        
        if self.statut == 'T' and self.date_fin is None:
            self.date_fin = timezone.now().date()
            
        super().save(*args, **kwargs)
        
        if self.statut == 'T':
            has_active = Affectation.objects.filter(
                vehicle=self.vehicle, 
                statut='A'
            ).exists()
            if not has_active:
                self.vehicle.statut = StatutVehicule.DISPONIBLE
                self.vehicle.save()

class ContractType(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nom du type')
    code = models.CharField(max_length=20, unique=True, verbose_name='Code')
    description = models.TextField(blank=True, verbose_name='Description')
    
    class Meta:
        verbose_name = 'Type de contrat'
        verbose_name_plural = 'Types de contrat'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Provider(models.Model):
    name = models.CharField(max_length=255, verbose_name='Nom du fournisseur')
    email = models.EmailField(blank=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Téléphone')
    address = models.TextField(blank=True, verbose_name='Adresse')
    
    class Meta:
        verbose_name = 'Fournisseur'
        verbose_name_plural = 'Fournisseurs'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Contract(models.Model):
    vehicle = models.ForeignKey('Vehicule', on_delete=models.CASCADE)
    contract_type = models.ForeignKey(ContractType, on_delete=models.PROTECT, related_name='contracts')
    provider = models.ForeignKey(Provider, on_delete=models.PROTECT)
    reference_number = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    expiration_date = models.DateField()
    contract_file = models.FileField(upload_to='parcauto/contracts/')
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.contract_type} - {self.vehicle} ({self.start_date} to {self.expiration_date})"
    
    @property
    def media_url(self):
        return f"{self.contract_file}"
    
    @property
    def is_expired(self):
        return self.expiration_date < date.today()

    @property
    def days_until_expiration(self):
        return (self.expiration_date - date.today()).days

    def get_status(self):
        if self.is_expired:
            return 'expired'
        elif self.days_until_expiration <= 30:
            return 'expiring'
        return 'active'