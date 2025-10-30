from django import forms
from decimal import Decimal

from apps.purchases.models.payment_mode import PaymentMode
from .models import Supplier, Country, City, Language, Tax, PurchaseOrder, PurchaseOrderLine, ConventionType, Convention, ConventionLine
from apps.inventory.models.unit_of_mesure import UnitOfMesure

# === Supplier Form ===
class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

# === Country Form ===
class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['name']

# === City Form ===
class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['name', 'country']

# === Language Form ===
class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = ['name']

# === Tax Form ===
class TaxForm(forms.ModelForm):
    class Meta:
        model = Tax
        fields = ['libelle', 'valeur']

# === Purchase Order Form ===
class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['name', 'partner', 'currency', 'date_order', 'state', 'notes', 'payment_mode']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'partner': forms.Select(attrs={'class': 'form-select'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'date_order': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'state': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'payment_mode': forms.Select(attrs={'class': 'form-select'}),
        }

# === Purchase Order Line Form ===
class PurchaseOrderLineForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderLine
        fields = ['product', 'product_qty', 'price_unit', 'price_subtotal', 'product_uom', 'tax', 'name']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'product_qty': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'price_unit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'price_subtotal': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True, 'step': '0.01'}),
            'tax': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['price_subtotal'].required = False  # ➕ ajouter cette ligne
        self.fields['price_subtotal'].widget.attrs['readonly'] = True
        self.fields['name'].required = False
        self.fields['tax'].required = False
        self.fields['product_uom'].required = False


    def clean(self):
        cleaned_data = super().clean()
        product_qty = cleaned_data.get('product_qty')
        price_unit = cleaned_data.get('price_unit')
        if product_qty is not None and price_unit is not None:
            cleaned_data['price_subtotal'] = (Decimal(str(product_qty)) * Decimal(str(price_unit))).quantize(Decimal('0.01'))
        return cleaned_data

# === Payment Mode Form ===
class PaymentModeForm(forms.ModelForm):
    class Meta:
        model = PaymentMode
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du mode de paiement'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description'}),
        }
class ConventionForm(forms.ModelForm):
    class Meta:
        model = Convention
        fields = [
            'name', 'partner', 'convention_type', 'currency',
            'date_start', 'date_end', 'state', 'general_conditions',
            'attachments', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'partner': forms.Select(attrs={'class': 'form-select'}),
            'convention_type': forms.Select(attrs={'class': 'form-select'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'date_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'state': forms.Select(attrs={'class': 'form-select'}),
            'general_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'attachments': forms.ClearableFileInput(attrs={'class': 'form-control', 'multiple': False}),  # ajuster 'multiple' selon usage
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ConventionLineForm(forms.ModelForm):
    class Meta:
        model = ConventionLine
        fields = ['product', 'product_qty', 'price_unit', 'price_subtotal', 'tax', 'name']  # ❌ product_uom retiré
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'product_qty': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'price_unit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'price_subtotal': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True, 'step': '0.01'}),
            'tax': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['price_subtotal'].required = False
        self.fields['price_subtotal'].widget.attrs['readonly'] = True
        self.fields['name'].required = False
        self.fields['tax'].required = False

    def clean(self):
        cleaned_data = super().clean()
        product_qty = cleaned_data.get('product_qty')
        price_unit = cleaned_data.get('price_unit')
        product = cleaned_data.get('product')

        if product_qty is not None and price_unit is not None:
            cleaned_data['price_subtotal'] = (Decimal(str(product_qty)) * Decimal(str(price_unit))).quantize(Decimal('0.01'))

        if product and not cleaned_data.get('name'):
            cleaned_data['name'] = str(product)

        return cleaned_data

# === Convention Type Form ===
class ConventionTypeForm(forms.ModelForm):
    class Meta:
        model = ConventionType
        fields = ['libelle']
        widgets = {
            'libelle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du type de convention'}),
        }