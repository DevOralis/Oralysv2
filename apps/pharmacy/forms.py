from django import forms
from decimal import Decimal

from .models.pharmaceutical_form import PharmaceuticalForm
from .models.supplier import PharmacySupplier
from .models.dci import Dci
from .models.pharmacy import Pharmacy
from .models.location_type import PharmacyLocationType
from .models.stock_location import PharmacyStockLocation
from .models.product import PharmacyProduct
from .models.product_location import PharmacyProductLocation
from .models import PharmacyOrder, PharmacyOrderLine
from .models.pharmacy_operation_type import PharmacyOperationType
from .models.pharmacy_stock_move import PharmacyStockMove
from .models.pharmacy_line_stock_move import PharmacyLineStockMove
from .models.pharmacy_product_category import PharmacyProductCategory
from .models.pharmacy_product_uom import PharmacyUnitOfMesure
from apps.purchases.models import Country, City, Language

class PharmacyProductCategoryForm(forms.ModelForm):
    class Meta:
        model = PharmacyProductCategory
        fields = ['label', 'description']
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'label': 'Libellé',
            'description': 'Description',
        }
class PharmacyUnitOfMesureForm(forms.ModelForm):
    class Meta:
        model = PharmacyUnitOfMesure
        fields = ['label', 'symbole']
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control'}),
            'symbole': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'label': 'Libellé',
            'symbole': 'Symbole',
        }
class PharmaceuticalFormForm(forms.ModelForm):
    class Meta:
        model = PharmaceuticalForm
        fields = ['name', 'description']
        labels = {
            'name': 'Libellé',
            'description': 'Description',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex. : Comprimé'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = PharmacySupplier
        fields = [
            'name', 'logo', 'is_company', 'street', 'street2', 'zip',
            'city', 'country', 'lang', 'email', 'phone', 'mobile',
            'ICE', 'RC', 'IF', 'vat', 'RIB', 'comment'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_company': forms.RadioSelect(choices=[(True, 'Oui'), (False, 'Non')]),
            'street': forms.TextInput(attrs={'class': 'form-control'}),
            'street2': forms.TextInput(attrs={'class': 'form-control'}),
            'zip': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.Select(attrs={'class': 'form-select'}),
            'country': forms.Select(attrs={'class': 'form-select'}),
            'lang': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'ICE': forms.TextInput(attrs={'class': 'form-control'}),
            'RC': forms.NumberInput(attrs={'class': 'form-control'}),
            'IF': forms.NumberInput(attrs={'class': 'form-control'}),
            'vat': forms.TextInput(attrs={'class': 'form-control'}),
            'RIB': forms.TextInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optionnel : personnaliser les queryset
        self.fields['city'].queryset = City.objects.all()
        self.fields['country'].queryset = Country.objects.all()
        self.fields['lang'].queryset = Language.objects.all()
        
        # Ajouter les options vides
        self.fields['city'].empty_label = "-- Sélectionnez une ville --"
        self.fields['country'].empty_label = "-- Sélectionnez un pays --"
        self.fields['lang'].empty_label = "-- Sélectionnez une langue --"

class DciForm(forms.ModelForm):
    class Meta:
        model = Dci
        fields = ['label', 'description']
        labels = {
            'label': 'Nom DCI',
            'description': 'Description',
        }
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom DCI'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows': 3}),
        }

class PharmacyForm(forms.ModelForm):
    class Meta:
        model = Pharmacy
        fields = ['label', 'adress']
        labels = {
            'label': 'Nom de la pharmacie',
            'adress': 'Adresse',
        }
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le nom de la pharmacie'}),
            'adress': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Entrez l\'adresse'}),
        }

class PharmacyOrderForm(forms.ModelForm):
    class Meta:
        model = PharmacyOrder
        fields = ['supplier', 'date_order', 'currency', 'state', 'payment_mode', 'notes', 'supplier_ref', 'name']
        widgets = {
            'name': forms.HiddenInput(),
            'date_order': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['name'].initial = self.instance.name
        if self.instance and self.instance.state != 'confirmed':
            self.fields['payment_mode'].disabled = True

class PharmacyOrderLineForm(forms.ModelForm):
    class Meta:
        model = PharmacyOrderLine
        fields = ['product', 'product_qty', 'price_unit', 'tax', 'price_subtotal', 'name']
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
        self.fields['product'].required = False
        self.fields['product_qty'].required = False
        self.fields['price_unit'].required = False
        self.fields['tax'].required = False
        self.fields['price_subtotal'].required = False
        self.fields['name'].required = False

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        qty = cleaned_data.get('product_qty')
        price = cleaned_data.get('price_unit')
        # Only validate if the line has data (new or modified)
        if product or qty is not None or price is not None:
            if not product:
                self.add_error('product', 'Ce champ est obligatoire pour une ligne valide.')
            if qty is None:
                self.add_error('product_qty', 'Ce champ est obligatoire pour une ligne valide.')
            if price is None:
                self.add_error('price_unit', 'Ce champ est obligatoire pour une ligne valide.')
            if qty is not None and qty <= 0:
                self.add_error('product_qty', 'La quantité doit être supérieure à 0.')
            if price is not None and price < 0:
                self.add_error('price_unit', 'Le prix unitaire ne peut pas être négatif.')
            # Calculate price_subtotal if valid
            if product and qty is not None and price is not None:
                cleaned_data['price_subtotal'] = (Decimal(str(qty)) * Decimal(str(price))).quantize(Decimal('0.01'))
        else:
            cleaned_data['price_subtotal'] = None  # Allow empty lines to pass
        return cleaned_data



class ProductForm(forms.ModelForm):
    total_quantity = forms.DecimalField(
        label='Quantité totale (tous les postes)',
        required=False,
        disabled=True,
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'readonly': 'readonly'}
        )
    )
    nombrepiece = forms.IntegerField(
        label='Nombre de pièces par boîte',
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_nombrepiece'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'short_label':
                field.required = False

        self.fields['dci'].empty_label = "Sélectionner DCI"
        self.fields['pharmaceutical_form'].empty_label = "Sélectionner forme pharmaceutique"
        self.fields['uom'].empty_label = "Sélectionner unité de mesure"
        self.fields['categ'].empty_label = "Sélectionner catégorie"
        if self.instance and self.instance.pk:
            self.fields['total_quantity'].initial = self.instance.total_quantity
        else:
            self.fields['total_quantity'].widget = forms.HiddenInput()

    class Meta:
        model = PharmacyProduct
        fields = [
            'short_label', 'brand', 'full_label', 'dci',
            'pharmaceutical_form', 'dosage', 'barcode', 'ppm_price',
            'unit_price', 'supplier_price', 'internal_purchase_price',
            'refund_price', 'refund_rate', 'uom', 'categ', 
            'total_quantity', 'nombrepiece'
        ]
        widgets = {
            'short_label': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'full_label': forms.TextInput(attrs={'class': 'form-control'}),
            'dci': forms.Select(attrs={'class': 'form-select'}),
            'pharmaceutical_form': forms.Select(attrs={'class': 'form-select'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control'}),
            'ppm_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'supplier_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'internal_purchase_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'refund_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'refund_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'uom': forms.Select(attrs={'class': 'form-select'}),
            'categ': forms.Select(attrs={'class': 'form-select'}),
            'nombrepiece': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_nombrepiece'}),
        }
        labels = {
            'short_label': 'Libellé court',
            'brand': 'Marque',
            'full_label': 'Libellé complet',
            'dci': 'DCI',
            'pharmaceutical_form': 'Forme pharmaceutique',
            'dosage': 'Dosage',
            'barcode': 'Code-barres',
            'ppm_price': 'Prix PPM',
            'unit_price': 'Prix unitaire',
            'supplier_price': 'Prix fournisseur',
            'internal_purchase_price': "Prix d'achat interne",
            'refund_price': 'Prix de remboursement',
            'refund_rate': 'Taux de remboursement',
            'uom': 'Unité de mesure',
            'categ': 'Catégorie',
            'nombrepiece': 'Nombre de pièces par boîte',
        }
class LocationTypeForm(forms.ModelForm):
    class Meta:
        model = PharmacyLocationType
        fields = ['name', 'description']
        labels = {
            'name': 'Nom',
            'description': 'Description',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
class StockLocationForm(forms.ModelForm):
    is_parent = forms.BooleanField(required=False, label="Est un poste racine", initial=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre parent_location et pharmacy optionnels
        self.fields['parent_location'].required = False
        self.fields['pharmacy'].required = False
        # location_type reste obligatoire
        self.fields['location_type'].required = True
    
    class Meta:
        model = PharmacyStockLocation
        fields = ['name', 'parent_location', 'location_type', 'pharmacy']
        labels = {
            'name': 'Nom de la location',
            'parent_location': 'Poste parent',
            'location_type': 'Type de location',
            'pharmacy': 'Pharmacie',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_location': forms.Select(attrs={'class': 'form-select'}),
            'location_type': forms.Select(attrs={'class': 'form-select'}),
            'pharmacy': forms.Select(attrs={'class': 'form-select'}),
        }
class ProductLocationForm(forms.ModelForm):
    class Meta:
        model = PharmacyProductLocation
        fields = ['location', 'quantity_stored']
        widgets = {
            'location':        forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'quantity_stored': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'last_count_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'quantity_counted': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),


        }
        labels = {
            'location':        'Location',
            'quantity_stored': 'Quantity',
            'quantity_counted': 'Quantité comptée',
            'last_count_date': 'Date du dernier inventaire',

        }
class OperationTypeForm(forms.ModelForm):
    class Meta:
        model = PharmacyOperationType
        fields = ['label']
        labels = {
            'label': 'Libellé',
        }
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PharmacyStockMoveForm(forms.ModelForm):
    class Meta:
        model = PharmacyStockMove
        fields = [
            'operation_type', 'source_location', 'dest_location',
            'department', 'supplier', 'notes', 'scheduled_date'
        ]
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-select', 'data-field': 'supplier'}),
            'source_location': forms.Select(attrs={'class': 'form-select', 'data-field': 'source'}),
            'dest_location': forms.Select(attrs={'class': 'form-select', 'data-field': 'dest'}),
            'department': forms.Select(attrs={'class': 'form-select', 'data-field': 'department'}),
            'scheduled_date': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'operation_type': forms.Select(attrs={'class': 'form-select', 'data-toggle': 'operation-type'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'supplier': 'Fournisseur',
            'source_location': "Poste d'origine",
            'dest_location': 'Poste de destination',
            'department': 'Département',
            'scheduled_date': 'Date planifiée',
            'operation_type': 'Type d\'opération',
            'notes': 'Notes',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['scheduled_date'].input_formats = ['%Y-%m-%d']

        # Personnalisation des placeholders pour les champs de sélection
        self.fields['operation_type'].empty_label = "Choisir une opération"
        self.fields['source_location'].empty_label = "Choisir un poste d'origine"
        self.fields['dest_location'].empty_label = "Choisir un poste de destination"
        self.fields['department'].empty_label = "Choisir un département"
        self.fields['supplier'].empty_label = "Choisir un fournisseur"

    def clean(self):
        cleaned_data = super().clean()
        source = cleaned_data.get('source_location')
        dest = cleaned_data.get('dest_location')
        department = cleaned_data.get('department')
        supplier = cleaned_data.get('supplier')
        operation_type = cleaned_data.get('operation_type')

        is_consumption = operation_type and 'consommation' in operation_type.label.lower()
        is_reception = operation_type and 'réception' in operation_type.label.lower()

        if is_consumption:
            if dest:
                self.add_error('dest_location', "Le poste de destination doit être vide pour un mouvement de consommation.")
            cleaned_data['dest_location'] = None
            if supplier:
                self.add_error('supplier', "Le fournisseur ne doit pas être utilisé pour les mouvements de consommation.")
            cleaned_data['supplier'] = None
        elif is_reception:
            if source:
                self.add_error('source_location', "Le poste d'origine doit être vide pour un mouvement de réception.")
            cleaned_data['source_location'] = None
            if department:
                self.add_error('department', "Le département ne doit pas être utilisé pour les mouvements de réception.")
            cleaned_data['department'] = None
        else:
            if department:
                self.add_error('department', "Le département ne doit être utilisé que pour les mouvements de consommation.")
            cleaned_data['department'] = None
            if supplier:
                self.add_error('supplier', "Le fournisseur ne doit être utilisé que pour les mouvements de réception.")
            cleaned_data['supplier'] = None

        if source and dest and source == dest and not is_reception:
            self.add_error('dest_location', "Le poste de destination doit être différent de le poste d'origine.")
        return cleaned_data

class PharmacyLineStockMoveForm(forms.ModelForm):
    class Meta:
        model = PharmacyLineStockMove
        fields = ['product', 'quantity_demanded', 'quantity_arrived', 'uom']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity_demanded': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity_arrived': forms.NumberInput(attrs={'class': 'form-control'}),
            'uom': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'product': 'Produit',
            'quantity_demanded': 'Quantité Demandée',
            'quantity_arrived': 'Quantité Arrivée',
            'uom': 'Unité de Mesure',
        }
