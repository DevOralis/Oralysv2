from django.db import models
from apps.hr.models import Department, Employee

# Create your models here.

class Offer(models.Model):
    title = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True, blank=True)
    publication_date = models.DateField(null=False)
    end_date = models.DateField(null=False)
    skills = models.TextField(null=True, blank=True)
    profile = models.TextField(null=True, blank=True, verbose_name="Profil recherché")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    positions_available = models.PositiveIntegerField(default=1, verbose_name="Nombre de postes")
    archived = models.BooleanField(default=False)

    class Meta:
        pass

    def __str__(self):
        return self.title

class Candidate(models.Model):
    last_name = models.CharField(max_length=100, null=False)
    first_name = models.CharField(max_length=100, null=False)
    email = models.CharField(max_length=255, null=False)
    phone = models.CharField(max_length=20, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    photo = models.ImageField(upload_to='recruitment/candidates/photos/', null=True, blank=True)
    linkedin_profile = models.URLField(max_length=500, null=True, blank=True)
    archived = models.BooleanField(default=False)

    class Meta:
        pass

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Application(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, null=False)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, null=False)
    submission_date = models.DateTimeField(null=False)
    source = models.CharField(max_length=255, null=True, blank=True)
    always_available = models.BooleanField(default=False)
    availability_start = models.DateField(null=True, blank=True)
    availability_end = models.DateField(null=True, blank=True)
    cv = models.FileField(upload_to='recruitment/applications/cv/', null=True, blank=True)
    cover_letter = models.FileField(upload_to='recruitment/applications/cover_letters/', null=True, blank=True)
    certificates = models.FileField(upload_to='recruitment/applications/certificates/', null=True, blank=True)
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('in_review', 'In Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=False)
    archived = models.BooleanField(default=False)

    class Meta:
        pass

class Interview(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, null=False)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    videcall_url = models.URLField(max_length=500, null=True, blank=True)
    organizer = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='organized_interviews')
    description = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    RESULT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('pending', 'Pending'),
    ]
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, null=True, blank=True)
    KANBAN_STAGES = [
        ('reception', "Réception de l'offre"),
        ('a', 'Entretien A'),
        ('b', 'Entretien B'),
    ]
    stage = models.CharField(max_length=20, choices=KANBAN_STAGES, default='reception')
    archived = models.BooleanField(default=False)
    class Meta:
        pass

class Pointage(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='pointages')
    date = models.DateField()
    jour = models.CharField(max_length=20)
    heure_arrivee = models.TimeField()
    heure_depart = models.TimeField()
    heure_travaillee = models.DurationField()

    def __str__(self):
        return f"{self.employee.full_name} - {self.date}"

class Evaluation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='evaluations')
    evaluator = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='evaluations_given')
    evaluation_date = models.DateField(auto_now_add=True)
    
    # Critères d'évaluation (notation 1-5)
    work_quality = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name="Qualité du travail")
    deadline_respect = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name="Respect des délais")
    team_spirit = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name="Esprit d'équipe")
    autonomy = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name="Autonomie")
    initiative = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name="Capacité d'initiative")
    
    # Note globale calculée
    overall_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    
    # Appréciation libre
    comments = models.TextField(verbose_name="Commentaires du supérieur", null=True, blank=True)
    improvement_plan = models.TextField(verbose_name="Plan d'amélioration", null=True, blank=True)
    
    # Statut de validation
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('submitted', 'Soumis'),
        ('validated', 'Validé'),
        ('signed', 'Signé'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Validation RH
    hr_validation = models.BooleanField(default=False, verbose_name="Validation RH")
    hr_validator = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='hr_validations')
    hr_validation_date = models.DateTimeField(null=True, blank=True)
    
    # Notification
    employee_notified = models.BooleanField(default=False, verbose_name="Salarié notifié")
    notification_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-evaluation_date']
        verbose_name = "Évaluation"
        verbose_name_plural = "Évaluations"
    
    def __str__(self):
        evaluator_name = self.evaluator.full_name if self.evaluator else "Système"
        return f"Évaluation de {self.employee.full_name} par {evaluator_name} - {self.evaluation_date}"
    
    def save(self, *args, **kwargs):
        # Calcul automatique de la note globale
        if self.work_quality and self.deadline_respect and self.team_spirit and self.autonomy and self.initiative:
            self.overall_score = (self.work_quality + self.deadline_respect + self.team_spirit + self.autonomy + self.initiative) / 5
        super().save(*args, **kwargs)