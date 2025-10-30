from django.db import models
from django.core.validators import MinValueValidator
from .employee import Employee
from .leave_type import LeaveType
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from decimal import Decimal
import json
import os

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('submitted', 'Soumis'),
        ('approved', 'Approuvé'),
        ('refused', 'Refusé'),
        ('canceled', 'Annulé'),
    ]
    
    request_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_requests',
        verbose_name="Employé"
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name='requests',
        verbose_name="Type de congé"
    )
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    reason = models.TextField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Statut"
    )
    request_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de demande"
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Commentaires"
    )
    certificate = models.FileField(
        upload_to='leave_certificates/',
        null=True,
        blank=True,
        verbose_name="Certificat médical"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Créé le"
    )
    selected_days = models.TextField(
        null=True,
        blank=True,
        verbose_name="Jours sélectionnés",
        help_text="Liste des dates sélectionnées au format JSON"
    )

    # --- Avis du chef de département ---
    MANAGER_DECISION_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('refused', 'Refusé'),
    ]
    manager_decision = models.CharField(
        max_length=10,
        choices=MANAGER_DECISION_CHOICES,
        default='pending',
        verbose_name="Décision chef"
    )
    manager_decision_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date décision chef"
    )
    manager_decider = models.ForeignKey(
        'Employee',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='manager_decisions',
        verbose_name="Chef décideur"
    )
    manager_comments = models.TextField(
        null=True,
        blank=True,
        verbose_name="Commentaires chef"
    )
    
    class Meta:
        verbose_name = "Demande de congé"
        verbose_name_plural = "Demandes de congés"
        db_table = 'hr_leave_request'
        ordering = ['-request_date']
    
    def __str__(self):
        return f"Congé {self.leave_type.name} - {self.employee.full_name} ({self.start_date} au {self.end_date})"
        
    def approve(self, approver, comments=None):
        """
        Approuve la demande de congé par l'approbateur spécifié
        """
        from .leave_approval import LeaveApproval
        from .leave_balance import LeaveBalance
        
        # Vérifier si la demande n'est pas déjà approuvée ou refusée
        if self.status in ['approved', 'refused']:
            return False
        
        # Créer l'approbation
        approval = LeaveApproval.objects.create(
            request=self,
            employee=approver,
            decision='approved',
            comments=comments
        )
        
        # Vérifier si c'est un congé ouvert (default_days nul ou zéro)
        is_open_leave = self.leave_type.default_days is None or self.leave_type.default_days == 0
        
        # Mettre à jour le solde de congés seulement si ce n'est pas un congé ouvert
        if not is_open_leave:
            # Mettre à jour le solde de congés
            current_year = self.start_date.year
            balance = LeaveBalance.objects.get(
                employee=self.employee,
                leave_type=self.leave_type,
                year=current_year
            )
            
            # Ajouter les jours aux jours pris et recalculer le solde
            balance.taken += self.duration
            # Le calcul de remaining sera fait automatiquement dans la méthode save()
            balance.save()
        
        # Mettre à jour le statut de la demande
        self.status = 'approved'
        self.save()
        
        return True
    
    def refuse(self, approver, comments=None):
        """
        Refuse la demande de congé par l'approbateur spécifié
        """
        from .leave_approval import LeaveApproval
        
        # Vérifier si la demande n'est pas déjà approuvée ou refusée
        if self.status in ['approved', 'refused']:
            return False
        
        # Créer l'approbation
        approval = LeaveApproval.objects.create(
            request=self,
            employee=approver,
            decision='refused',
            comments=comments
        )
        
        # Mettre à jour le statut de la demande
        self.status = 'refused'
        self.save()
        
        return True

    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError("La date de début doit être antérieure à la date de fin.")
            
            # Vérifier les jours sélectionnés
            if self.selected_days:
                try:
                    selected_dates = json.loads(self.selected_days)
                    
                    # Vérifier les weekends et jours fériés
                    for date_str in selected_dates:
                        date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        # Les vérifications spécifiques ont été supprimées car les attributs n'existent pas
                        
                except json.JSONDecodeError:
                    raise ValidationError("Le format des jours sélectionnés est invalide.")
                
            # Vérifier le type de fichier du certificat
            if self.certificate:
                ext = os.path.splitext(self.certificate.name)[1].lower().lstrip('.')
                allowed_types = ['pdf', 'jpg', 'jpeg', 'png']  # Types de fichiers autorisés par défaut
                if ext not in allowed_types:
                    raise ValidationError(f"Le type de fichier {ext} n'est pas autorisé. Types autorisés : {', '.join(allowed_types)}")

    def get_moroccan_holidays(self, year):
        """Retourne les jours fériés fixes au Maroc pour une année donnée"""
        return [
            f"{year}-01-01",  # Nouvel An
            f"{year}-01-11",  # Manifeste de l'Indépendance
            f"{year}-05-01",  # Fête du Travail
            f"{year}-07-30",  # Fête du Trône
            f"{year}-08-14",  # Allégeance Oued Eddahab
            f"{year}-08-20",  # Révolution du Roi et du Peuple
            f"{year}-08-21",  # Fête de la Jeunesse
            f"{year}-11-06",  # Marche Verte
            f"{year}-11-18",  # Fête de l'Indépendance
        ]

    def is_weekend(self, date):
        """Vérifie si une date tombe un weekend (samedi=5 ou dimanche=6)"""
        return date.weekday() in [5, 6]

    def is_holiday(self, date):
        """Vérifie si une date est un jour férié"""
        date_str = date.strftime('%Y-%m-%d')
        holidays = self.get_moroccan_holidays(date.year)
        
        # Si la date est à cheval sur deux années, vérifier aussi l'année suivante
        if date.month == 12:
            holidays.extend(self.get_moroccan_holidays(date.year + 1))
        elif date.month == 1:
            holidays.extend(self.get_moroccan_holidays(date.year - 1))
            
        return date_str in holidays

    @property
    def duration(self):
        """Calcule la durée en jours ouvrables selon les jours sélectionnés ou automatiquement"""
        if not self.start_date or not self.end_date:
            return Decimal('0')

        # Si des jours spécifiques ont été sélectionnés, utiliser cette liste
        if self.selected_days:
            try:
                selected_dates = json.loads(self.selected_days)
                return Decimal(str(len(selected_dates)))
            except (json.JSONDecodeError, TypeError):
                # En cas d'erreur avec le JSON, revenir à la méthode standard
                pass
                
        # Méthode standard: compter tous les jours entre start_date et end_date selon la configuration
        duration = Decimal('0')
        current_date = self.start_date
        
        while current_date <= self.end_date:
            # Vérifier si le jour est un jour de travail selon la configuration
            if self.leave_type.is_working_day(current_date.weekday()):
                # Ne pas compter les jours fériés
                if not self.is_holiday(current_date):
                    duration += Decimal('1')
            current_date += timedelta(days=1)

        return duration

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
        # La mise à jour du solde est maintenant gérée uniquement dans la méthode approve()
        # et dans la vue approve_leave_request pour éviter les doublons

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_status = self.status 