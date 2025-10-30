from django import forms
from .models import Incident, Equipement

class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['equipement', 'date_declaration', 'type', 'statut', 'description']
        widgets = {
            'equipement': forms.Select(attrs={
                'class': 'form-select border-2',
                'required': True
            }),
            'date_declaration': forms.DateTimeInput(attrs={
                'class': 'form-control border-2',
                'type': 'datetime-local',
                'required': True
            }),
            'type': forms.Select(attrs={
                'class': 'form-select border-2',
                'required': True
            }),
            'statut': forms.Select(attrs={
                'class': 'form-select border-2',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control border-2',
                'rows': 4,
                'placeholder': 'Décrivez l\'incident...'
            }),
        }
        labels = {
            'equipement': 'Équipement *',
            'date_declaration': 'Date de déclaration *',
            'type': 'Type d\'incident *',
            'statut': 'Statut *',
            'description': 'Description',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipement'].queryset = Equipement.objects.all()
        self.fields['equipement'].empty_label = "-- Sélectionnez un équipement --"
        
       
        self.fields['type'].choices = [('', '-- Sélectionnez --')] + list(Incident.TYPE_CHOICES)
        self.fields['statut'].choices = [('', '-- Sélectionnez --')] + list(Incident.STATUT_CHOICES)

    def clean_date_declaration(self):
        date_declaration = self.cleaned_data.get('date_declaration')
        if not date_declaration:
            raise forms.ValidationError("La date de déclaration est obligatoire.")
        return date_declaration

    def clean_equipement(self):
        equipement = self.cleaned_data.get('equipement')
        if not equipement:
            raise forms.ValidationError("Vous devez sélectionner un équipement.")
        return equipement