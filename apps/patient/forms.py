from django import forms
from .models import Payment, Acte

class ActeForm(forms.ModelForm):
    class Meta:
        model = Acte
        fields = ['libelle', 'price']
        widgets = {
            'libelle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Libellé de l\'acte'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Prix'
            })
        }
        labels = {
            'libelle': 'Libellé',
            'price': 'Prix (DH)'
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'journal',
            'payment_channel', 
            'payment_mode',
            'beneficiary_account',
            'amount',
            'payment_date',
            'memo'
        ]
        widgets = {
            'journal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Journal de paiement'
            }),
            'payment_channel': forms.Select(attrs={
                'class': 'form-select'
            }),
            'payment_mode': forms.Select(attrs={
                'class': 'form-select'
            }),
            'beneficiary_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Compte bancaire du bénéficiaire'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'payment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'memo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mémo du paiement'
            })
        }
        labels = {
            'journal': 'Journal',
            'payment_channel': 'Canal de paiement',
            'payment_mode': 'Mode de paiement',
            'beneficiary_account': 'Compte bancaire du bénéficiaire',
            'amount': 'Montant',
            'payment_date': 'Date de règlement',
            'memo': 'Mémo'
        }