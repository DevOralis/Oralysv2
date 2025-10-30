from django import forms
from .models import MenuPersonnalise, MenuSupplementaire, ProgrammeJourMenu, Plat, ProgrammeJour, Programme, MenuStandard

REPAS_CHOICES = [
    ('Petit déjeuner', 'Petit déjeuner (07h00)'),
    ('Déjeuner', 'Déjeuner (12h30)'),
    ('Collation', 'Collation (16h30)'),
    ('Dîner', 'Dîner (20h00)'),
]

# Formulaire pour MenuStandard
class MenuStandardForm(forms.ModelForm):
    class Meta:
        model = MenuStandard
        fields = ['date', 'repas', 'plats']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

# Formulaire pour Programme
class ProgrammeForm(forms.ModelForm):
    
    date_debut = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'id_date_debut'
        }),
        label='Date de début'
    )
    
    date_fin = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'id_date_fin'
        }),
        label='Date de fin'
    )
    
    class Meta:
        model = Programme
        fields = ['nom', 'date_debut', 'date_fin', 'lieu']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_nom'}),
            'lieu': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_lieu'}),
        }

# Formulaire pour ProgrammeJour
class ProgrammeJourForm(forms.ModelForm):
    class Meta:
        model = ProgrammeJour
        fields = ['date', 'menu']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'id_date'
            }),
            'menu': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_menu'
            }),
        }

class ProgrammeJourMenuForm(forms.ModelForm):
    """Formulaire pour la configuration séquentielle des menus par jour de programme"""
    
    class Meta:
        model = ProgrammeJourMenu
        fields = ['plats', 'heure_service', 'description']
        widgets = {
            'plats': forms.SelectMultiple(attrs={
                'class': 'form-control select2-multiple',
                'data-placeholder': 'Sélectionnez un ou plusieurs plats...',
                'multiple': 'multiple',
                'data-allow-clear': 'true',
                'data-tags': 'true',
                'data-token-separators': '[",", " "]'
            }),
            'heure_service': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'placeholder': 'HH:MM'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Notes spéciales pour ce menu (ex: sans gluten, client spécial, etc.)...'
            }),
        }

    def __init__(self, *args, **kwargs):
        programme_jour = kwargs.pop('programme_jour', None)
        super().__init__(*args, **kwargs)
        
        # Personnaliser le queryset des plats si nécessaire
        if programme_jour:
            # Ici on pourrait ajouter une logique pour filtrer les plats selon le contexte
            pass
        
        # Améliorer l'affichage des plats avec recherche
        self.fields['plats'].queryset = Plat.objects.all().order_by('nom')
        self.fields['plats'].help_text = "Sélectionnez un ou plusieurs plats pour composer ce menu"

class MenuPersonnaliseForm(forms.ModelForm):
    class Meta:
        model = MenuPersonnalise
        fields = ['client', 'num_chambre', 'date', 'repas', 'quantite', 'plats', 'description']
        widgets = {
            'client': forms.Select(attrs={
                'class': 'form-control select2',
            }),
            'num_chambre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro de chambre'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'repas': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
            'plats': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'Description ou remarques spéciales...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].empty_label = "Nom du patient "
        for field_name, field in self.fields.items():
            if field_name == 'client':
                field.widget.attrs['class'] = 'form-control select2'
            elif field_name == 'plats':
                 field.widget.attrs['class'] = 'form-control select2'
            else:
                field.widget.attrs['class'] = 'form-control'


class MenuSupplementaireForm(forms.ModelForm):
    class Meta:
        model = MenuSupplementaire
        fields = ['client', 'num_chambre', 'date', 'repas', 'quantite']
        widgets = {
            'client': forms.Select(attrs={
                'class': 'form-control select2',
                'id': 'client',
            }),
            'num_chambre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro de chambre'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'repas': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].empty_label = "Nom du patient"
        for field_name, field in self.fields.items():
            if field_name == 'client':
                field.widget.attrs['class'] = 'form-control select2'
            else:
                field.widget.attrs['class'] = 'form-control'

