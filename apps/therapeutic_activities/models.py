from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Count, Q
from apps.hr.models.employee import Employee
from apps.patient.models import Patient


class ActivityType(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Type d\'activité'
        verbose_name_plural = 'Types d\'activités'

    def __str__(self):
        return self.name

    @property
    def activities_count(self):
        """Nombre d'activités de ce type"""
        return self.activity_set.count()

    @property
    def sessions_count(self):
        """Nombre de sessions de ce type d'activité"""
        return Session.objects.filter(activity__type=self).count()


class ActivityLocation(models.Model):
    name        = models.CharField(max_length=255, unique=True)
    address     = models.CharField(max_length=255, blank=True)
    capacity    = models.PositiveIntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Salle d\'activité'
        verbose_name_plural = 'Salles d\'activités'

    def __str__(self):
        return self.name

    @property
    def sessions_count(self):
        """Nombre de sessions dans cette salle"""
        return self.session_set.count()

    @property
    def upcoming_sessions(self):
        """Sessions à venir dans cette salle"""
        return self.session_set.filter(
            date__gte=timezone.now().date(),
            status='planned'
        ).order_by('date', 'start_time')

    def clean(self):
        if self.capacity < 0:
            raise ValidationError("La capacité ne peut pas être négative.")
        super().clean()


class Activity(models.Model):
    title       = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    type        = models.ForeignKey(ActivityType, on_delete=models.PROTECT, null=True, blank=True)
    coach       = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'position__name__iexact': 'coach'}
    )
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Activité'
        verbose_name_plural = 'Activités'

    def __str__(self):
        return self.title

    @property
    def sessions_count(self):
        """Nombre de sessions pour cette activité"""
        return self.sessions.count()

    @property
    def upcoming_sessions(self):
        """Sessions à venir pour cette activité"""
        return self.sessions.filter(
            date__gte=timezone.now().date(),
            status='planned'
        ).order_by('date', 'start_time')

    @property
    def total_participants(self):
        """Nombre total de participants pour cette activité"""
        return Participation.objects.filter(session__activity=self).count()

    def clean(self):
        if self.coach and self.coach.position:
            if self.coach.position.name.lower() != "coach":
                raise ValidationError("L'employé sélectionné n'a pas la position 'Coach'.")
        elif self.coach:
            raise ValidationError("Le coach sélectionné n'a pas de position définie.")
        super().clean()


class Session(models.Model):
    STATUS_CHOICES = [
        ('planned',  'Prévu'),
        ('done',     'Réalisé'),
        ('canceled', 'Annulé'),
    ]

    activity         = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='sessions')
    location         = models.ForeignKey(ActivityLocation, on_delete=models.PROTECT)
    date             = models.DateField()
    start_time       = models.TimeField()
    end_time         = models.TimeField()
    max_participants = models.PositiveIntegerField(default=0)
    status           = models.CharField(max_length=10, choices=STATUS_CHOICES, default='planned')
    notes            = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'start_time']
        unique_together = [('location', 'date', 'start_time', 'end_time')]
        verbose_name = 'Session'
        verbose_name_plural = 'Sessions'

    def __str__(self):
        return f"{self.activity.title} @ {self.date} {self.start_time}-{self.end_time}"

    @property
    def duration_minutes(self):
        """Durée de la session en minutes"""
        if self.start_time and self.end_time:
            start_minutes = self.start_time.hour * 60 + self.start_time.minute
            end_minutes = self.end_time.hour * 60 + self.end_time.minute
            return end_minutes - start_minutes
        return 0

    @property
    def participants_count(self):
        """Nombre de participants inscrits"""
        return self.participants.count()

    @property
    def available_spots(self):
        """Nombre de places disponibles"""
        return max(0, self.max_participants - self.participants_count)

    @property
    def is_full(self):
        """La session est-elle complète ?"""
        return self.participants_count >= self.max_participants

    @property
    def is_past(self):
        """La session est-elle passée ?"""
        return self.date < timezone.now().date()

    @property
    def is_today(self):
        """La session est-elle aujourd'hui ?"""
        return self.date == timezone.now().date()

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("L'heure de fin doit être après l'heure de début.")

        # Vérification des chevauchements coach
        overlapping_coach = Session.objects.filter(
            activity__coach=self.activity.coach,
            date=self.date
        ).exclude(pk=self.pk).filter(
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )
        if overlapping_coach.exists():
            raise ValidationError("Ce coach a déjà une séance à cet horaire.")

        # Vérification des chevauchements salle
        overlapping_loc = Session.objects.filter(
            location=self.location,
            date=self.date
        ).exclude(pk=self.pk).filter(
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )
        if overlapping_loc.exists():
            raise ValidationError("La salle est déjà réservée à cet horaire.")

        # Vérification de la capacité
        if self.max_participants > self.location.capacity:
            raise ValidationError(
                f"Le nombre max de participants ({self.max_participants}) "
                f"dépasse la capacité de la salle ({self.location.capacity})."
            )

        super().clean()


class Participation(models.Model):
    STATUS_CHOICES = [
        ('present', 'Présent'),
        ('absent',  'Absent'),
        ('excused', 'Excusé'),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE
    )
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='participants')
    status  = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    notes   = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('patient', 'session')]
        ordering = ['session__date', 'session__start_time']
        verbose_name = 'Participation'
        verbose_name_plural = 'Participations'

    def __str__(self):
        return f"{self.patient} → {self.session}"

    @property
    def has_evaluation(self):
        """Le patient a-t-il une évaluation ergothérapique ?"""
        return hasattr(self, 'ergo_eval')

    @property
    def has_coaching(self):
        """Le patient a-t-il une session de coaching ?"""
        return hasattr(self, 'coaching')

    @property
    def has_social_report(self):
        """Le patient a-t-il un rapport social ?"""
        return hasattr(self, 'social_report')

    def clean(self):
        # Vérification que le patient n'est pas déjà inscrit
        existing = Participation.objects.filter(
            patient=self.patient, 
            session=self.session
        ).exclude(pk=self.pk)
        
        if existing.exists():
            raise ValidationError("Ce patient est déjà inscrit à cette session.")
        
        super().clean()


class ErgotherapyEvaluation(models.Model):
    participation     = models.OneToOneField(
        Participation, 
        on_delete=models.CASCADE, 
        related_name='ergo_eval'
    )
    rosenberg_score   = models.FloatField(null=True, blank=True)
    moca_score        = models.FloatField(null=True, blank=True)
    osa_result        = models.TextField(blank=True)
    goals             = models.TextField(blank=True)
    evaluation_date   = models.DateField(auto_now_add=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Évaluation ergothérapique'
        verbose_name_plural = 'Évaluations ergothérapiques'

    def __str__(self):
        return f"ErgoEval for {self.participation}"

    def clean(self):
        if self.rosenberg_score is not None and (self.rosenberg_score < 0 or self.rosenberg_score > 100):
            raise ValidationError("Le score Rosenberg doit être entre 0 et 100.")
        
        if self.moca_score is not None and (self.moca_score < 0 or self.moca_score > 30):
            raise ValidationError("Le score MoCA doit être entre 0 et 30.")
        
        super().clean()


class CoachingSession(models.Model):
    participation = models.OneToOneField(
        Participation, 
        on_delete=models.CASCADE, 
        related_name='coaching'
    )
    plan          = models.TextField(blank=True)
    result        = models.TextField(blank=True)
    session_date  = models.DateField(auto_now_add=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Session de coaching'
        verbose_name_plural = 'Sessions de coaching'

    def __str__(self):
        return f"Coaching for {self.participation}"


class SocialReport(models.Model):
    participation     = models.OneToOneField(
        Participation, 
        on_delete=models.CASCADE, 
        related_name='social_report'
    )
    intervention_plan = models.TextField(blank=True)
    interview_notes   = models.TextField(blank=True)
    exit_summary      = models.TextField(blank=True)
    meeting_notes     = models.TextField(blank=True)
    report_date       = models.DateField(auto_now_add=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Rapport social'
        verbose_name_plural = 'Rapports sociaux'

    def __str__(self):
        return f"SocialReport for {self.participation}"
