from django.db import models
from django.core.validators import RegexValidator
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from .emergency_contact import EmergencyContact

# Validator pour CIN (N° carte d'identité)
CINValidator = RegexValidator(
    regex=r'^$|^[A-Z0-9]{8,20}$',
    message="Le N° CIN doit contenir 8 à 20 caractères alphanumériques."
)

class Patient(models.Model):
    # Identifiants
    patient_identifier = models.CharField(
        "Identifiant patient", max_length=50, unique=True, blank=True, null=True
    )
    cin                = models.CharField(
        "N° CIN", max_length=20, unique=True, validators=[CINValidator], blank=True, null=True
    )
    passport_number    = models.CharField(
        "N° de passeport", max_length=20, unique=True, blank=True, null=True
    )

    # Informations personnelles
    last_name    = models.CharField("Nom", max_length=100, blank=True, null=True)
    first_name   = models.CharField("Prénom", max_length=100, blank=True, null=True)
    gender       = models.CharField(
        "Sexe", max_length=1,
        choices=[('H', 'H'), ('F', 'F'), ('O', 'Autre')],
        blank=True, null=True
    )
    birth_date   = models.DateField("Date de naissance", blank=True, null=True)
    nationality  = CountryField("Nationalité", blank=True)
    profession   = models.CharField("Profession", max_length=100, blank=True)
    city         = models.CharField("Ville", max_length=100, blank=True)
    email        = models.EmailField("Email", blank=True)

    # Contacts
    phone              = PhoneNumberField("Téléphone fixe", blank=True)
    mobile_number      = PhoneNumberField("GSM", blank=True)
    emergency_contacts = models.ManyToManyField(
        EmergencyContact,
        verbose_name="Contacts d'urgence",
        blank=True
    )
    spouse_name        = models.CharField("Conjoint(e)", max_length=100, blank=True)

    # Médecins
    treating_physician = models.CharField(
        "Médecin traitant", max_length=100, blank=True, null=True
    )
    referring_physician = models.CharField(
        "Médecin correspondant", max_length=100, blank=True, null=True
    )
    disease_speciality = models.CharField(
        "Type maladie", max_length=100, blank=True, null=True
    )

    has_insurance = models.BooleanField("A une mutuelle/assurance", default=False)
    insurance_number = models.CharField("N° immatriculation", max_length=50, blank=True, null=True)
    affiliation_number = models.CharField("N° affiliation", max_length=50, blank=True, null=True)
    relationship = models.CharField("Lien de parenté", max_length=50, blank=True, null=True)
    insured_name = models.CharField("Nom de l'adhérent", max_length=100, blank=True, null=True)
    
    # Source d'acquisition du patient
    source = models.CharField("Source", max_length=200, blank=True, null=True, help_text="Source d'acquisition du patient (ex: Réseaux, recommandation, autre)")
    
    # Notes médicales
    medical_notes = models.TextField("Notes médicales", blank=True, null=True, help_text="Notes et commentaires concernant le dossier médical")

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = "Patient"
        verbose_name_plural = "Patients"

    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.patient_identifier or "Patient"
    
    def get_full_name(self):
        """Retourne le nom complet du patient"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.patient_identifier or "Patient"

