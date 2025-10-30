from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import os
from apps.hr.models import Employee
from apps.purchases.models import Supplier
import json
from django.conf import settings

# Create your models here.
    
    
# Fonctions utilitaires pour la configuration
def get_config_file_path():
    """Retourne le chemin du fichier de configuration"""
    formation_app_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(formation_app_dir, 'formation_config.json')

def load_formation_config():
    """Charge la configuration depuis le fichier JSON"""
    config_file = get_config_file_path()
    default_config = {
        'formation_types': [
            {'value': 'interne', 'label': 'Interne'},
            {'value': 'externe', 'label': 'Externe'},
            {'value': 'e_learning', 'label': 'E-learning'},
        ],
        'formation_domaines': [
            {'value': 'IT', 'label': 'Informatique'},
            {'value': 'HR', 'label': 'Ressources Humaines'},
            {'value': 'Finance', 'label': 'Finance'},
            {'value': 'life', 'label': 'Life'},
            {'value': 'economie', 'label': 'Économie'},
            {'value': 'medecine', 'label': 'Médecine'},
            {'value': 'management', 'label': 'Management'},
            {'value': 'qualite', 'label': 'Qualité'},
            {'value': 'securite', 'label': 'Sécurité'},
            {'value': 'marketing', 'label': 'Marketing'},
        ]
    }
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return default_config
    except Exception as e:
        print(f"Erreur lors du chargement de la configuration: {e}")
        return default_config

def get_type_choices():
    """Retourne les choix de types depuis la configuration"""
    config = load_formation_config()
    return [(item['value'], item['label']) for item in config.get('formation_types', [])]

def get_domaine_choices():
    """Retourne les choix de domaines depuis la configuration"""
    config = load_formation_config()
    return [(item['value'], item['label']) for item in config.get('formation_domaines', [])]


class Formation(models.Model):
    """
    Entité Formation - Définition d'une formation
    """
    """"
    TYPE_CHOICES = [
        ('interne', 'Interne'),
        ('externe', 'Externe'),
        ('e_learning', 'E-learning'),
    ]

    DOMAINE_CHOICES = [
        ('IT', 'Informatique'),
        ('HR', 'Ressources Humaines'),
        ('Finance', 'Finance'),
        ('life', 'Life'),
        ('economie', 'Économie'),
        ('medecine', 'Médecine'),
        ('management', 'Management'),
        ('qualite', 'Qualité'),
        ('securite', 'Sécurité'),
        ('marketing', 'Marketing'),
    ]
    """
    # Propriétés dynamiques pour les choices
    @property
    def TYPE_CHOICES(self):
        return get_type_choices()
    
    @property  
    def DOMAINE_CHOICES(self):
        return get_domaine_choices()
    
    code = models.CharField(max_length=10, primary_key=True)  # Code unique alphanumérique
    titre = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=15)
    duree_heures = models.IntegerField(validators=[MinValueValidator(1)])  # > 0
    cout = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, 
                              validators=[MinValueValidator(0)])  # ≥ 0
    domaine = models.CharField(max_length=100, null=True, blank=True)
    # prestataire = models.ForeignKey(Prestataire, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='formations')

    def get_type_display(self):
        """Méthode personnalisée pour l'affichage du type"""
        type_choices = dict(self.TYPE_CHOICES)
        return type_choices.get(self.type, self.type)
    
    def get_domaine_display(self):
        """Méthode personnalisée pour l'affichage du domaine"""
        domaine_choices = dict(self.DOMAINE_CHOICES)
        return domaine_choices.get(self.domaine, self.domaine)
    
    def __str__(self):
        return f"{self.code} - {self.titre}"


class Collaborateur(models.Model):
    """
    Entité Collaborateur - Importée du module RH
    """
    # id est automatiquement créé par Django (AutoField)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    service = models.CharField(max_length=100, null=True, blank=True)  # Ex. Administratif, Soins
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
class Formateur(models.Model):
    """
    Entité Formateur - Personne habilitée à donner des formations
    """
    # id est automatiquement créé par Django (AutoField)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    service = models.CharField(max_length=100, null=True, blank=True)  # Ex. Administratif, Soins
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
    class Meta:
        db_table = 'formation_formateur'
        verbose_name = 'Formateur'
        verbose_name_plural = 'Formateurs'


class Session(models.Model):
    """
    Entité Session - Session de formation planifiée
    """
    STATUT_CHOICES = [
        ('planifiée', 'Planifiée'),
        ('en_cours', 'En cours'),
        ('terminée', 'Terminée'),
        ('annulée', 'Annulée'),
    ]
    
    # id est automatiquement créé par Django (AutoField)
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, to_field='code')
    formateur = models.ForeignKey(Formateur, on_delete=models.CASCADE)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    lieu = models.CharField(max_length=255, null=True, blank=True)
    places_totales = models.IntegerField(validators=[MinValueValidator(1)])  # ≥ 1
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES)
    
    
    def __str__(self):
        return f"Session {self.formation.titre} - {self.date_debut.strftime('%Y-%m-%d')}"


class Inscription(models.Model):
    """
    Entité Inscription - Inscription d'un collaborateur à une session
    """
    STATUT_CHOICES = [
        ('inscrit', 'Inscrit'),
        ('present', 'Présent'),
        ('absent', 'Absent'),
        ('annulé', 'Annulé'),
    ]
    
    # id est automatiquement créé par Django (AutoField)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    # collaborateur = models.ForeignKey(Collaborateur, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES)
    date_inscription = models.DateTimeField(default=timezone.now)  # par défaut = NOW
    
    def __str__(self):
        return f"{self.employee} - {self.session}"


class Evaluation(models.Model):
    """
    Entité Évaluation - Évaluation d'une inscription
    """
    # id est automatiquement créé par Django (AutoField)
    inscription = models.ForeignKey(Inscription, on_delete=models.CASCADE)
    score = models.IntegerField(null=True, blank=True, 
                               validators=[MinValueValidator(0), MaxValueValidator(100)])  # Entre 0 et 100
    commentaires = models.TextField(null=True, blank=True)
    date_evaluation = models.DateTimeField()
    
    def __str__(self):
        return f"Évaluation {self.inscription.collaborateur} - {self.inscription.session.formation.titre}"


