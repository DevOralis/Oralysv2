from django import forms
from .models import Admission, Room, Bed, Reservation, Companion,bed_status, room_type

class AdmissionForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = [
            'patient', 'consultation', 'admission_date', 'assignment_mode',
            'room', 'bed', 'room_type', 'discharge_date', 'discharge_reason', 'notes'
        ]
        labels = {
            'patient': 'Patient',
            'consultation': 'Consultation',
            'admission_date': 'Date d\'admission',
            'assignment_mode': 'Mode d\'affectation',
            'room': 'Chambre',
            'bed': 'Lit',
            'room_type': 'Type de chambre',
            'discharge_date': 'Date de sortie',
            'discharge_reason': 'Motif de sortie',
            'notes': 'Observations',
        }
        widgets = {
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
            'discharge_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bed'].required = False
        self.fields['room'].required = False
        self.fields['bed'].empty_label = "Non assigné"
        self.fields['room'].empty_label = "Non assignée"

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_id', 'room_name', 'room_type', 'capacity', 'status', 'description']
        widgets = {
            'room_id': forms.HiddenInput(attrs={'id': 'room-id-field'}),
            'room_name': forms.TextInput(attrs={'id': 'id_room_name', 'class': 'form-control', 'placeholder': 'Nom de la chambre'}),
            'room_type': forms.Select(attrs={'id': 'id_room_type', 'class': 'form-select', 'title': 'Choisir un type'}),
            'capacity': forms.NumberInput(attrs={'id': 'id_capacity', 'class': 'form-control', 'placeholder': 'Nombre de personnes', 'min': '1'}),
            'status': forms.Select(attrs={'id': 'id_status', 'class': 'form-select', 'title': 'Choisir un statut'}),
            'description': forms.Textarea(attrs={'id': 'id_description', 'class': 'form-control', 'rows': '3', 'placeholder': 'Description de la chambre...'}),
        }
        labels = {
            'room_id': 'Identifiant de la chambre',
            'room_name': 'Nom de la chambre',
            'room_type': 'Type de chambre',
            'capacity': 'Capacité',
            'status': 'Statut',
            'description': 'Description',
        }

class BedForm(forms.ModelForm):
    class Meta:
        model = Bed
        fields = ['bed_number', 'room', 'bed_status']
        labels = {
            'room': 'Chambre',
            'bed_number': 'Numéro du lit',
            'bed_status': 'Statut du lit',
        }
        widgets = {
            'room': forms.Select(attrs={'class': 'form-select', 'id': 'id_room'}),
            'bed_number': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_bed_number', 'placeholder': 'Ex: 101, 102, etc.'}),
            'bed_status': forms.Select(attrs={'class': 'form-select', 'id': 'id_bed_status'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Récupérer toutes les chambres disponibles
        self.fields['room'].queryset = Room.objects.all()
        self.fields['room'].empty_label = "Sélectionner une chambre"
        
        # Récupérer tous les statuts de lit disponibles
        from .models.bed_status import BedStatus
        self.fields['bed_status'].queryset = BedStatus.objects.all()
        self.fields['bed_status'].empty_label = "Sélectionner un statut"
        
        # Rendre les champs obligatoires
        self.fields['bed_number'].required = True
        self.fields['room'].required = True
        self.fields['bed_status'].required = True


class BedStatusForm(forms.ModelForm):
    class Meta:
        model = bed_status.BedStatus
        fields = ['name']
        labels = {
            'name': 'Nom du statut',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_name'}),
        }

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['patient', 'room', 'bed', 'start_date', 'end_date', 'reservation_status']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'room': forms.Select(attrs={'class': 'form-select'}),
            'bed': forms.Select(attrs={'class': 'form-select', 'data-placeholder': 'Non assigné'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reservation_status': forms.Select(attrs={'class': 'form-select'}),
        }
    labels = {
        'patient': 'Patient',
        'room': 'Chambre',
        'bed': 'Lit',
        'start_date': 'Date de début',
        'end_date': 'Date de fin',
        'reservation_status': 'Statut de la réservation',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bed'].required = False
        self.fields['room'].required = False
        self.fields['bed'].empty_label = "Non assigné"
        self.fields['room'].empty_label = "Non assignée"

class CompanionForm(forms.ModelForm):
    class Meta:
        model = Companion
        fields = [
            'patient', 'companion_name', 'relationship', 'start_date',
            'end_date', 'room', 'bed', 'accommodation_start_date', 'accommodation_end_date', 'notes'
        ]
        labels = {
            'patient': 'Patient',
            'companion_name': 'Nom de l\'accompagnant',
            'relationship': 'Lien de parenté',
            'start_date': 'Date de début',
            'end_date': 'Date de fin',
            'room': 'Chambre',
            'bed': 'Lit',
            'accommodation_start_date': 'Début de l\'hébergement',
            'accommodation_end_date': 'Fin de l\'hébergement',
            'notes': 'Remarques',
        }
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select', 'id': 'id_patient'}),
            'companion_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_companion_name'}),
            'relationship': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_relationship'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_start_date'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_end_date'}),
            'room': forms.Select(attrs={'class': 'form-select', 'id': 'id_room'}),
            'bed': forms.Select(attrs={'class': 'form-select', 'id': 'id_bed'}),
            'accommodation_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_accommodation_start_date'}),
            'accommodation_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_accommodation_end_date'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'id': 'id_notes'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make sure we're filtering correctly using the proper field references
        try:
            # Filter beds by status name 'available' - this is the correct way
            from .models.bed_status import BedStatus
            available_status = BedStatus.objects.get(name='available')
            self.fields['bed'].queryset = Bed.objects.filter(bed_status=available_status)
        except BedStatus.DoesNotExist:
            # Fallback: show all beds if 'available' status doesn't exist
            self.fields['bed'].queryset = Bed.objects.all()
        except Exception as e:
            # Log the error and show all beds as fallback
            print(f"Error filtering beds in CompanionForm: {e}")
            self.fields['bed'].queryset = Bed.objects.all()
        
        try:
            # Filter rooms by status 'available'
            self.fields['room'].queryset = Room.objects.filter(status='available')
        except Exception as e:
            # Fallback: show all rooms
            print(f"Error filtering rooms in CompanionForm: {e}")
            self.fields['room'].queryset = Room.objects.all()
        
        # Make bed and room fields optional
        self.fields['bed'].required = False
        self.fields['room'].required = False
        self.fields['bed'].empty_label = "Non assigné"
        self.fields['room'].empty_label = "Non assignée"
class RoomTypeForm(forms.ModelForm):
    class Meta:
        model = room_type.RoomType
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

