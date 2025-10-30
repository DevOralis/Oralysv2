# models.py
from django.db import models
from django.utils import timezone
from apps.hr.models import Department
from apps.purchases.models import Supplier



class Priorite(models.Model):
    nom = models.CharField(max_length=20, unique=True)
    niveau = models.PositiveSmallIntegerField(default=0, help_text="Ordre de tri")
    
    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Priorité"
        verbose_name_plural = "Priorités"
        ordering = ['niveau']


class Statut(models.Model):
    CATEGORY_CHOICES = [
        ('active', 'Active'),
        ('terminated', 'Terminée'),
        ('cancelled', 'Annulée'),
        ('pending', 'En attente'),
    ]
    nom = models.CharField(max_length=30, unique=True)
    couleur = models.CharField(max_length=20, blank=True, help_text="CSS class: success, warning, danger")
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='active',
        help_text="Utilisé pour le regroupement dans les statistiques"
    )
    
    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Statut"
        verbose_name_plural = "Statuts"

class Produit(models.Model):
    TYPE_DEMANDE_CHOICES = [
        ('Interne', 'Interne'),
        ('Patient', 'Patient'),
    ]
    nom = models.CharField("Nom du produit", max_length=100)
    description = models.TextField("Description", blank=True)
    image = models.ImageField("Image", upload_to="produits/", blank=True, null=True)
    type_demande = models.CharField("Type de demande", max_length=20, choices=TYPE_DEMANDE_CHOICES)
    disponible = models.BooleanField("Disponible", default=True)
    
    def __str__(self):
        return f"{self.nom} ({self.type_demande})"

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['nom']


class DemandePatientModel(models.Model):
    nom = models.CharField("Nom", max_length=100)
    prenom = models.CharField("Prénom", max_length=100)
    date_naissance = models.DateField("Date de naissance", null=True, blank=True)
    sexe = models.CharField("Sexe", max_length=1, choices=[('M', 'Masculin'), ('F', 'Féminin')], blank=True)
    chambre = models.CharField("Chambre", max_length=10, blank=True)
    telephone = models.CharField("Téléphone", max_length=20, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"

    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"
        ordering = ['nom', 'prenom']


class Demande(models.Model):
    priorite = models.ForeignKey(Priorite, on_delete=models.CASCADE)
    statut = models.ForeignKey(Statut, on_delete=models.CASCADE)
    description = models.CharField("Description", max_length=200)
    prestataire = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    date_souhaitee = models.DateTimeField("Date souhaitée", null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']
        verbose_name = "Demande"
        verbose_name_plural = "Demandes"

    def get_type_display(self):
        if isinstance(self, DemandeInterne):
            return "Interne"
        elif isinstance(self, DemandePatient):
            return "Patient"
        return "Inconnu"


class DemandeInterne(Demande):
    departement_source = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='demandes_internes_envoyees',
        verbose_name="Département source"
    )
    departement_destinataire = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='demandes_internes_recues',
        verbose_name="Département destinataire"
    )

    def __str__(self):
        return f"[Interne] {self.description}"

    class Meta:
        verbose_name = "Demande Interne"
        verbose_name_plural = "Demandes Internes"


class DemandePatient(Demande):
    patient = models.ForeignKey(
        DemandePatientModel,
        on_delete=models.CASCADE,
        verbose_name="Patient"
    )

    def __str__(self):
        return f"[Patient] {self.description}"

    class Meta:
        verbose_name = "Demande Patient"
        verbose_name_plural = "Demandes Patient"


class DemandeProduit(models.Model):
    # Only one of these can be set
    demande_interne = models.ForeignKey(
        DemandeInterne,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='produits_dans_demande'
    )
    demande_patient = models.ForeignKey(
        DemandePatient,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='produits_dans_demande'
    )
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField("Quantité", default=1)

    def clean(self):
        from django.core.exceptions import ValidationError
        # Ensure exactly one is set
        if bool(self.demande_interne) == bool(self.demande_patient):
            raise ValidationError(
                'Le produit doit être lié à UNE demande (Interne OU Patient), pas les deux ni aucune.'
            )

    def save(self, *args, **kwargs):
        self.full_clean()  # Call clean() before saving
        super().save(*args, **kwargs)

    def __str__(self):
        if self.demande_interne:
            return f"{self.quantite}x {self.produit.nom} → Demande Interne #{self.demande_interne.id}"
        if self.demande_patient:
            return f"{self.quantite}x {self.produit.nom} → Demande Patient #{self.demande_patient.id}"
        return "Erreur: Aucune demande liée"

    class Meta:
        verbose_name = "Produit dans demande"
        verbose_name_plural = "Produits dans demandes"