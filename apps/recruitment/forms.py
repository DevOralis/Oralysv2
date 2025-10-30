from django import forms
from .models import Candidate


class MultiFileInput(forms.ClearableFileInput):
    """Widget that supports selecting multiple files."""
    allow_multiple_selected = True

class SingleCVUploadForm(forms.Form):
    """Form for uploading a single CV file"""
    cv_file = forms.FileField(
        label="Fichier CV",
        help_text="Sélectionnez un fichier PDF",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf',
            'id': 'single-cv-file'
        })
    )
    
    def clean_cv_file(self):
        file = self.cleaned_data.get('cv_file')
        if file:
            if not file.name.lower().endswith('.pdf'):
                raise forms.ValidationError("Seuls les fichiers PDF sont acceptés.")
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError("Le fichier est trop volumineux. Taille maximum : 10MB.")
        return file

class MultipleCVUploadForm(forms.Form):
    """Form for uploading multiple CV files"""
    cv_files = forms.FileField(
        label="Fichiers CV",
        help_text="Sélectionner plusieurs fichiers PDF",
        widget=MultiFileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf',
            'id': 'multiple-cv-files',
            'multiple': True,
        })
    )
    
    def clean_cv_files(self):
        # This method won't be used for multiple files - validation is done in the view
        # Return empty list to avoid Django form validation issues
        return []

class CandidatePreviewForm(forms.ModelForm):
    """Form for previewing and editing extracted candidate data"""
    class Meta:
        model = Candidate
        fields = ['last_name', 'first_name', 'email', 'phone', 'birth_date', 'address', 'gender', 'linkedin_profile']
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(
                choices=[('', '-- Sélectionner --'), ('Homme', 'Homme'), ('Femme', 'Femme')],
                attrs={'class': 'form-control'}
            ),
            'linkedin_profile': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/...'})
        }
