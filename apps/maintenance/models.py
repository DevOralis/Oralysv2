import qrcode
from io import BytesIO
from django.core.files import File
from django.utils import timezone
from django.db import models
from django.urls import reverse, reverse_lazy
from apps.purchases.models import Supplier


class TypeMaintenance(models.Model):
    code = models.CharField(max_length=50, unique=True)
    libelle = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.libelle}"

class Convention(models.Model):
    TYPE_CHOICES = (
        ('préventive', 'Préventive'),
        ('corrective', 'Corrective'),
    )

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='maintenance_conventions', null=True, blank=True)
    type_convention = models.CharField(max_length=20, choices=TYPE_CHOICES)
    type_maintenance = models.ForeignKey(TypeMaintenance, on_delete=models.CASCADE, null=True, blank=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    description = models.TextField(blank=True, null=True)
    cout_mensuel = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    fichier = models.FileField(upload_to='conventions/', null=True, blank=True)

    class Meta:
        verbose_name = "Convention"
        verbose_name_plural = "Conventions"
        ordering = ['-date_debut']

    def __str__(self):
        return f"{self.get_type_convention_display()} - {self.supplier.nom} ({self.date_debut} to {self.date_fin})"
    

class Visiteur(models.Model):
    nom = models.CharField(max_length=255, verbose_name="Nom")
    prenom = models.CharField(max_length=255, verbose_name="Prénom")
    email = models.EmailField(null=True, blank=True, verbose_name="Email")
    telephone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Téléphone")
    date_entree = models.DateTimeField(auto_now_add=True, verbose_name="Date d'entrée")
    date_sortie = models.DateTimeField(null=True, blank=True, verbose_name="Date de sortie")
    motif_visite = models.TextField(null=True, blank=True, verbose_name="Motif de visite")
    qr_code = models.ImageField(upload_to='visiteurs_qr/', null=True, blank=True, verbose_name="Code QR")
    
    class Meta:
        verbose_name = "Visiteur"
        verbose_name_plural = "Visiteurs"
        ordering = ['-date_entree']  # Most recent first
    
    def __str__(self):
        return f"{self.nom} {self.prenom}"
    
    def generate_qr_code(self):
        """Génère un code QR unique contenant les informations du visiteur"""
        if not self.qr_code:  # Ne générer que si pas déjà généré
            # Créer les données pour le QR code
            qr_data = {
                'nom': self.nom,
                'prenom': self.prenom,
                'date_entree': self.date_entree.strftime('%d/%m/%Y %H:%M'),
                'motif_visite': self.motif_visite or 'Non spécifié',
                'visiteur_id': self.id
            }
            
            # Convertir en JSON string
            import json
            qr_text = json.dumps(qr_data, ensure_ascii=False)
            
            # Générer le QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_text)
            qr.make(fit=True)
            
            # Créer l'image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Sauvegarder dans un buffer
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Créer le nom du fichier
            filename = f'visiteur_{self.id}_{self.nom}_{self.prenom}_qr.png'
            
            # Sauvegarder le fichier
            self.qr_code.save(filename, File(buffer), save=False)
    
    def save(self, *args, **kwargs):
        # Sauvegarder d'abord pour obtenir l'ID
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Générer le QR code seulement si c'est un nouveau visiteur ou si le QR code n'existe pas
        if is_new or not self.qr_code:
            self.generate_qr_code()
            # Sauvegarder à nouveau pour enregistrer le QR code
            super().save(update_fields=['qr_code'])
    
    @property
    def is_present(self):
        """Check if visitor is still present (no exit date)"""
        return self.date_sortie is None
    
    @property
    def visit_duration(self):
        """Calculate visit duration"""
        if self.date_sortie:
            return self.date_sortie - self.date_entree
        else:
            return timezone.now() - self.date_entree
    
    def duree_formatee(self):
        """Retourne une durée formatée en heures et minutes"""
        delta = self.visit_duration
        total_seconds = int(delta.total_seconds())
        heures = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        if heures:
            return f"{heures}h {minutes}min"
        return f"{minutes}min"

class Equipement(models.Model):
    nom = models.CharField(max_length=255)
    reference = models.CharField(max_length=100, unique=True)
    date_acquisition = models.DateField()
    emplacement = models.CharField(max_length=255)
    etat_choices = [
        ('neuf', 'Neuf'),
        ('bon', 'Bon état'),
        ('moyen', 'État moyen'),
        ('mauvais', 'Mauvais état'),
        ('hors_service', 'Hors service'),
    ]
    etat = models.CharField(max_length=20, choices=etat_choices, default='bon')
    
    def __str__(self):
        return f"{self.nom} ({self.reference})"



class Incident(models.Model):
    equipement = models.ForeignKey('Equipement', on_delete=models.CASCADE, related_name='incidents')
    date_declaration = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True)
    
    TYPE_CHOICES = [
        ('panne', 'Panne'),
        ('maintenance', 'Maintenance'),
        ('accident', 'Accident'),
        ('defaillance', 'Défaillance'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='panne')
    
    STATUT_CHOICES = [
        ('ouvert', 'Ouvert'),
        ('en_cours', 'En cours'),
        ('resolu', 'Résolu'),
        ('ferme', 'Fermé'),
    ]
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ouvert')
    
    GRAVITE_CHOICES = [
        ('faible', 'Faible'),
        ('moyenne', 'Moyenne'),
        ('haute', 'Haute'),
    ]
    gravite = models.CharField(max_length=20, choices=GRAVITE_CHOICES, default='faible')
    
    def __str__(self):
        return f"Incident {self.id} sur {self.equipement.nom} - {self.statut}"
    
    def get_absolute_url(self):
        return reverse('maintenance:incident_list')
    
    def get_statut_badge_class(self):
        """Return Bootstrap badge class based on status"""
        badge_classes = {
            'ouvert': 'danger',
            'en_cours': 'info',
            'resolu': 'success',
            'ferme': 'secondary',
        }
        return badge_classes.get(self.statut, 'secondary')
    
    def get_type_display(self):
        """Get human-readable type"""
        return dict(self.TYPE_CHOICES).get(self.type, self.type)
    
    def get_statut_display(self):
        """Get human-readable status"""
        return dict(self.STATUT_CHOICES).get(self.statut, self.statut)
    
    def get_gravite_display(self):
        """Get human-readable gravity"""
        return dict(self.GRAVITE_CHOICES).get(self.gravite, self.gravite)
    
    def get_gravite_badge_class(self):
        """Return Bootstrap badge class based on gravity"""
        badge_classes = {
            'faible': 'secondary',
            'moyenne': 'warning',
            'haute': 'danger',
        }
        return badge_classes.get(self.gravite, 'secondary')
    
    def get_type_badge_class(self):
        """Return Bootstrap badge class based on type"""
        badge_classes = {
            'panne': 'info',
            'maintenance': 'info',
            'accident': 'info',
            'defaillance': 'info',
        }
        return badge_classes.get(self.type, 'secondary')
    
    class Meta:
        ordering = ['-date_declaration']


class Intervention(models.Model):
    equipement = models.ForeignKey(Equipement, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    date_intervention = models.DateTimeField()
    type_intervention = models.CharField(
        max_length=20,
        choices=[('preventive', 'Préventive'), ('corrective', 'Corrective')],
        default='preventive'
    )
    criticite = models.CharField(
        max_length=10,
        choices=[('faible', 'Faible'), ('moyenne', 'Moyenne'), ('haute', 'Haute')],
        default='moyenne'
    )
    description = models.TextField(blank=True, null=True)
    statut = models.CharField(max_length=20, choices=[
        ('planifiee', 'Planifiée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
    ], default='planifiee')

    def __str__(self):
        return f"{self.equipement.nom} - {self.date_intervention}"
    
    def get_type_intervention_display(self):
        """Get human-readable type intervention"""
        return dict(self._meta.get_field('type_intervention').choices).get(self.type_intervention, self.type_intervention)
    
    def get_criticite_display(self):
        """Get human-readable criticite"""
        return dict(self._meta.get_field('criticite').choices).get(self.criticite, self.criticite)
    
    def get_statut_display(self):
        """Get human-readable statut"""
        return dict(self._meta.get_field('statut').choices).get(self.statut, self.statut)
    
    def get_type_intervention_badge_class(self):
        """Return Bootstrap badge class based on type intervention"""
        badge_classes = {
            'preventive': 'info',
            'corrective': 'warning',
        }
        return badge_classes.get(self.type_intervention, 'secondary')
    
    def get_criticite_badge_class(self):
        """Return Bootstrap badge class based on criticite"""
        badge_classes = {
            'faible': 'success',
            'moyenne': 'warning',
            'haute': 'danger',
        }
        return badge_classes.get(self.criticite, 'secondary')
    
    def get_statut_badge_class(self):
        """Return Bootstrap badge class based on statut"""
        badge_classes = {
            'planifiee': 'primary',
            'en_cours': 'info',
            'terminee': 'success',
        }
        return badge_classes.get(self.statut, 'secondary')
    
    class Meta:
        ordering = ['-date_intervention']