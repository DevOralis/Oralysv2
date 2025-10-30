from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.hr.models.employee import Employee
from apps.patient.models import Patient
from .models import (
    ActivityType, ActivityLocation, Activity, Session, 
    Participation, ErgotherapyEvaluation, CoachingSession, SocialReport
)


# ========================================
# FORMULAIRES DE BASE (CONFIGURATION)
# ========================================
class ActivityTypeForm(forms.ModelForm):
    class Meta:
        model = ActivityType
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Nom du type d\'activité',
            'description': 'Description',
            'is_active': 'Actif',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Vérifier l'unicité (sauf pour l'instance actuelle)
            existing = ActivityType.objects.filter(name__iexact=name)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError("Un type d'activité avec ce nom existe déjà.")
        return name


class ActivityLocationForm(forms.ModelForm):
    class Meta:
        model = ActivityLocation
        fields = ['name', 'address', 'capacity', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Nom de la salle',
            'address': 'Adresse',
            'capacity': 'Capacité maximale',
            'is_active': 'Actif',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Vérifier l'unicité (sauf pour l'instance actuelle)
            existing = ActivityLocation.objects.filter(name__iexact=name)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError("Une salle avec ce nom existe déjà.")
        return name

    def clean_capacity(self):
        capacity = self.cleaned_data.get('capacity')
        if capacity is not None and capacity < 0:
            raise ValidationError("La capacité ne peut pas être négative.")
        return capacity

# ========================================
# FORMULAIRES D'ACTIVITÉS
# ========================================
class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['title', 'description', 'type', 'coach', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'coach': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'Titre de l\'activité',
            'description': 'Description',
            'type': 'Type d\'activité',
            'coach': 'Coach/Prestataire',
            'is_active': 'Actif',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les employés qui ont la position "Coach"
        self.fields['coach'].queryset = Employee.objects.filter(
            position__name__iexact='coach'
        ).order_by('full_name')
        self.fields['type'].empty_label = "Sélectionner un type"
        self.fields['coach'].empty_label = "Sélectionner un coach/prestataire"
        
        # Filtrer les types actifs
        self.fields['type'].queryset = ActivityType.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        coach = cleaned_data.get('coach')
        
        if coach and coach.position:
            if coach.position.name.lower() != "coach":
                self.add_error('coach', "L'employé sélectionné n'a pas la position 'Coach'.")
        elif coach:
            self.add_error('coach', "Le coach sélectionné n'a pas de position définie.")
        
        return cleaned_data

# ========================================
# FORMULAIRES DE SESSIONS
# ========================================
class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = [
            'activity', 'location', 'date', 'start_time', 
            'end_time', 'max_participants', 'status', 'notes'
        ]
        widgets = {
            'activity': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date',
                'min': timezone.now().date().isoformat()
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control', 
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control', 
                'type': 'time'
            }),
            'max_participants': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 1
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'activity': 'Activité',
            'location': 'Salle',
            'date': 'Date',
            'start_time': 'Heure de début',
            'end_time': 'Heure de fin',
            'max_participants': 'Nombre max de participants',
            'status': 'Statut',
            'notes': 'Notes',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['activity'].empty_label = "Sélectionner une activité"
        self.fields['location'].empty_label = "Sélectionner une salle"
        
        # Filtrer les activités actives
        self.fields['activity'].queryset = Activity.objects.filter(is_active=True)
        # Filtrer les salles actives
        self.fields['location'].queryset = ActivityLocation.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        location = cleaned_data.get('location')
        max_participants = cleaned_data.get('max_participants')
        date = cleaned_data.get('date')
        activity = cleaned_data.get('activity')
        
        # Vérification des heures
        if start_time and end_time and end_time <= start_time:
            self.add_error('end_time', "L'heure de fin doit être après l'heure de début.")
        
        # Vérification de la date
        if date and date < timezone.now().date():
            self.add_error('date', "La date ne peut pas être dans le passé.")
        
        # Vérification de la capacité
        if location and max_participants and max_participants > location.capacity:
            self.add_error('max_participants', 
                f"Le nombre max de participants ({max_participants}) "
                f"dépasse la capacité de la salle ({location.capacity})."
            )
        
        # Vérification des chevauchements (si on a toutes les données nécessaires)
        if all([date, start_time, end_time, location, activity]):
            # Vérification chevauchement coach
            overlapping_coach = Session.objects.filter(
                activity__coach=activity.coach,
                date=date
            ).exclude(pk=self.instance.pk if self.instance.pk else None).filter(
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            if overlapping_coach.exists():
                self.add_error(None, "Ce coach a déjà une séance à cet horaire.")
            
            # Vérification chevauchement salle
            overlapping_loc = Session.objects.filter(
                location=location,
                date=date
            ).exclude(pk=self.instance.pk if self.instance.pk else None).filter(
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            if overlapping_loc.exists():
                self.add_error(None, "La salle est déjà réservée à cet horaire.")
        
        return cleaned_data

# ========================================
# FORMULAIRES DE PARTICIPATION
# ========================================
class ParticipationForm(forms.ModelForm):
    class Meta:
        model = Participation
        fields = ['patient', 'session', 'status', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'session': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'patient': 'Patient',
            'session': 'Session',
            'status': 'Statut de présence',
            'notes': 'Notes',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient'].empty_label = "Sélectionner un patient"
        self.fields['session'].empty_label = "Sélectionner une session"
        
        # Assurer que le queryset des patients est défini
        self.fields['patient'].queryset = Patient.objects.all().order_by('last_name', 'first_name')
        
        # Filtrer les sessions à venir ou d'aujourd'hui
        self.fields['session'].queryset = Session.objects.select_related(
            'activity', 'location'
        ).filter(
            date__gte=timezone.now().date()
        ).order_by('date', 'start_time')

    def clean(self):
        cleaned_data = super().clean()
        patient = cleaned_data.get('patient')
        session = cleaned_data.get('session')
        
        # Vérification que le patient n'est pas déjà inscrit
        if patient and session:
            existing = Participation.objects.filter(
                patient=patient, 
                session=session
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            
            if existing.exists():
                self.add_error(None, "Ce patient est déjà inscrit à cette session.")
            
            # Vérification que la session n'est pas complète (temporairement désactivée)
            # if session and session.is_full:
            #     self.add_error('session', "Cette session est complète.")
        
        return cleaned_data

# ========================================
# FORMULAIRES D'ÉVALUATIONS SPÉCIALISÉES
# ========================================

class ErgotherapyEvaluationForm(forms.ModelForm):
    class Meta:
        model = ErgotherapyEvaluation
        fields = ['rosenberg_score', 'moca_score', 'osa_result', 'goals']
        widgets = {
            'rosenberg_score': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.1', 
                'min': '0', 
                'max': '100',
                'placeholder': 'Score entre 0 et 100'
            }),
            'moca_score': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.1', 
                'min': '0', 
                'max': '30',
                'placeholder': 'Score entre 0 et 30'
            }),
            'osa_result': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Résultats de l\'évaluation OSA'
            }),
            'goals': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Objectifs thérapeutiques définis'
            }),
        }
        labels = {
            'rosenberg_score': 'Score Rosenberg',
            'moca_score': 'Score MoCA',
            'osa_result': 'Résultat OSA',
            'goals': 'Objectifs thérapeutiques',
        }

    def clean_rosenberg_score(self):
        score = self.cleaned_data.get('rosenberg_score')
        if score is not None and (score < 0 or score > 100):
            raise ValidationError("Le score Rosenberg doit être entre 0 et 100.")
        return score

    def clean_moca_score(self):
        score = self.cleaned_data.get('moca_score')
        if score is not None and (score < 0 or score > 30):
            raise ValidationError("Le score MoCA doit être entre 0 et 30.")
        return score

class CoachingSessionForm(forms.ModelForm):
    class Meta:
        model = CoachingSession
        fields = ['plan', 'result']
        widgets = {
            'plan': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Plan de coaching détaillé'
            }),
            'result': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Résultats obtenus et observations'
            }),
        }
        labels = {
            'plan': 'Plan de coaching',
            'result': 'Résultats obtenus',
        }

class SocialReportForm(forms.ModelForm):
    class Meta:
        model = SocialReport
        fields = ['intervention_plan', 'interview_notes', 'exit_summary', 'meeting_notes']
        widgets = {
            'intervention_plan': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Plan d\'intervention social'
            }),
            'interview_notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Notes d\'entretien avec le patient'
            }),
            'exit_summary': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Résumé de sortie et recommandations'
            }),
            'meeting_notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Notes de réunion avec l\'équipe'
            }),
        }
        labels = {
            'intervention_plan': 'Plan d\'intervention',
            'interview_notes': 'Notes d\'entretien',
            'exit_summary': 'Résumé de sortie',
            'meeting_notes': 'Notes de réunion',
        }

# ========================================
# FORMULAIRES DE RECHERCHE ET FILTRAGE
# ========================================

class SessionSearchForm(forms.Form):
    activity = forms.ModelChoiceField(
        queryset=Activity.objects.filter(is_active=True),
        required=False,
        empty_label="Toutes les activités",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    location = forms.ModelChoiceField(
        queryset=ActivityLocation.objects.filter(is_active=True),
        required=False,
        empty_label="Toutes les salles",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[('', 'Tous les statuts')] + Session.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date de début"
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date de fin"
    )

class ParticipationSearchForm(forms.Form):
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.all(),
        required=False,
        empty_label="Tous les patients",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    session = forms.ModelChoiceField(
        queryset=Session.objects.all(),
        required=False,
        empty_label="Toutes les sessions",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[('', 'Tous les statuts')] + Participation.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

# ========================================
# FORMULAIRES DE MASSE (BULK OPERATIONS)
# ========================================

class BulkParticipationForm(forms.Form):
    patients = forms.ModelMultipleChoiceField(
        queryset=Patient.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Sélectionner les patients"
    )
    session = forms.ModelChoiceField(
        queryset=Session.objects.filter(date__gte=timezone.now().date()),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Session"
    )
    default_status = forms.ChoiceField(
        choices=Participation.STATUS_CHOICES,
        initial='present',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Statut par défaut"
    )

    def clean(self):
        cleaned_data = super().clean()
        patients = cleaned_data.get('patients')
        session = cleaned_data.get('session')
        
        if patients and session:
            # Vérifier qu'aucun patient n'est déjà inscrit
            existing_participations = Participation.objects.filter(
                patient__in=patients,
                session=session
            )
            if existing_participations.exists():
                existing_patients = [p.patient for p in existing_participations]
                raise ValidationError(
                    f"Les patients suivants sont déjà inscrits à cette session: "
                    f"{', '.join([str(p) for p in existing_patients])}"
                )
            
            # Vérifier que la session a assez de places
            if session and (session.participants_count + len(patients)) > session.max_participants:
                available_spots = session.available_spots
                raise ValidationError(
                    f"La session n'a que {available_spots} place(s) disponible(s) "
                    f"pour {len(patients)} patient(s) sélectionné(s)."
                )
        
        return cleaned_data
