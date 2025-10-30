from django.db import models
from django.urls import reverse


class Appointment(models.Model):
    STATUT_CHOICES = [
        ('à venir', 'À venir'),
        ('effectué', 'Effectué'),
        ('annulé', 'Annulé'),
    ]
    
    MODE_CHOICES = [
        ('telephone', 'Téléphone'),
        ('mail', 'Mail'),
        ('direct', 'Direct'),
    ]
    
    nom = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nom"
    )
    
    prenom = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Prénom"
    )
    
    telephone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Téléphone"
    )
    
    email = models.EmailField(
        blank=True,
        verbose_name="Email"
    )
    
    date_heure = models.DateTimeField(
        verbose_name="Date et heure du rendez-vous"
    )
    
    motif = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Motif du rendez-vous"
    )
    
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='à venir',
        verbose_name="Statut"
    )
    
    mode = models.CharField(
        max_length=20,
        choices=MODE_CHOICES,
        default='direct',
        verbose_name="Mode de prise de rendez-vous"
    )
    
    medecin = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        related_name='appointments',
        verbose_name="Médecin"
    )
    
    patient = models.ForeignKey(
        'patient.Patient',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='appointments',
        verbose_name="Patient"
    )
    
    class Meta:
        verbose_name = "Rendez-vous"
        verbose_name_plural = "Rendez-vous"
        ordering = ['-date_heure']
    
    def __str__(self):
        if self.patient:
            return f"{self.patient.last_name} {self.patient.first_name} - {self.date_heure.strftime('%d/%m/%Y %H:%M')}"
        else:
            return f"{self.nom} {self.prenom} - {self.date_heure.strftime('%d/%m/%Y %H:%M')}"
    
    def get_absolute_url(self):
        return reverse('patient:appointment_detail', kwargs={'pk': self.pk})
    
    @property
    def nom_complet(self):
        """Retourne le nom complet du patient ou du rendez-vous"""
        if self.patient:
            return f"{self.patient.last_name} {self.patient.first_name}"
        else:
            return f"{self.nom} {self.prenom}"
    
    @property
    def est_a_venir(self):
        """Vérifie si le rendez-vous est à venir"""
        return self.statut == 'à venir'
    
    @property
    def est_effectue(self):
        """Vérifie si le rendez-vous a été effectué"""
        return self.statut == 'effectué'
    
    @property
    def est_annule(self):
        """Vérifie si le rendez-vous a été annulé"""
        return self.statut == 'annulé'

