from django import forms
from .models.product import Product
from .models.category import Category
from .models.unit_of_mesure import UnitOfMesure
from .models.location_type import LocationType
from .models.stock_location import StockLocation
from .models.product_type import ProductType
from .models.operation_type import OperationType
from .models.stock_move import StockMove
from .models.line_stock_move import LineStockMove
from .models.product_location import ProductLocation


class ProductForm(forms.ModelForm):
    total_quantity = forms.DecimalField(
        label='Quantité totale (tous les emplacements)',
        required=False, disabled=True,
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'readonly': 'readonly'}
        )
    )

    class Meta:
        model = Product
        fields = [
            'name', 'default_code', 'standard_price', 'barcode',
            'categ', 'uom', 'weight', 'volume', 'dlc', 'stock_minimal',
            'description', 'active', 'image_1920', 'product_type',
            'total_quantity',
        ]
        exclude = ['default_code']
        widgets = {
            'name':              forms.TextInput(attrs={'class': 'form-control'}),
            'standard_price':    forms.NumberInput(attrs={'class': 'form-control'}),
            'barcode':           forms.TextInput(attrs={'class': 'form-control'}),
            'categ':             forms.Select(attrs={'class': 'form-select'}),
            'uom':               forms.Select(attrs={'class': 'form-select'}),
            'weight':            forms.NumberInput(attrs={'class': 'form-control'}),
            'volume':            forms.NumberInput(attrs={'class': 'form-control'}),
            'dlc':               forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'stock_minimal':     forms.NumberInput(attrs={'class': 'form-control'}),
            'description':       forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'image_1920':        forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'active':            forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'product_type':      forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'name': 'Nom du Produit :',
            'default_code': 'Référence interne :',
            'categ': 'Catégorie :',
            'barcode': 'Code-barres :',
            'standard_price': 'Coût standard :',
            'description': 'Description :',
            'active': 'Actif :',
            'weight': 'Poids :',
            'volume': 'Volume :',
            'dlc': 'DLC :',
            'stock_minimal': 'Stock minimal :',
            'uom': 'Unité de mesure :',
            'image_1920': 'Image principale :',
            'product_type': 'Type de produit :',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categ'].empty_label = "Choisir catégorie"
        self.fields['uom'].empty_label = "Choisir unité de mesure"
        self.fields['product_type'].empty_label = "Choisir type de produit"
        # Pre-fill total qty only when editing
        if self.instance and self.instance.pk:
            self.fields['total_quantity'].initial = self.instance.total_quantity
        else:
            self.fields['total_quantity'].widget = forms.HiddenInput()
            
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['label', 'description']
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'label': 'Libellé',
        }

class UnitOfMesureForm(forms.ModelForm):
    class Meta:
        model = UnitOfMesure
        fields = ['label', 'symbole']
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control'}),
            'symbole': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'label': 'Libellé',
            'symbole': 'Symbole',
        }

class ProductLocationForm(forms.ModelForm):
    class Meta:
        model = ProductLocation
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

class LocationTypeForm(forms.ModelForm):
    class Meta:
        model = LocationType
        fields = ['label', 'description']
        labels = {
            'label': 'Libellé',
        }
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class StockLocationForm(forms.ModelForm):
    is_parent = forms.BooleanField(required=False, label="Est un emplacement racine", initial=False)

    class Meta:
        model = StockLocation
        fields = ['name', 'location_type', 'parent_location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location_type': forms.Select(attrs={'class': 'form-select'}),
            'parent_location': forms.Select(attrs={'class': 'form-select'}),
        }
class ProductTypeForm(forms.ModelForm):
    class Meta:
        model = ProductType
        fields = ['label']
        labels = {
            'label': 'Libellé',
        }
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control'}),
        }

class OperationTypeForm(forms.ModelForm):
    class Meta:
        model = OperationType
        fields = ['label']
        labels = {
            'label': 'Libellé',
        }
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control'}),
        }
class StockMoveForm(forms.ModelForm):
    class Meta:
        model = StockMove
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
            'source_location': "Emplacement d'origine",
            'dest_location': 'Emplacement de destination',
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
        self.fields['source_location'].empty_label = "Choisir un emplacement d'origine"
        self.fields['dest_location'].empty_label = "Choisir un emplacement de destination"
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
                self.add_error('dest_location', "L'emplacement de destination doit être vide pour un mouvement de consommation.")
            cleaned_data['dest_location'] = None
            if supplier:
                self.add_error('supplier', "Le fournisseur ne doit pas être utilisé pour les mouvements de consommation.")
            cleaned_data['supplier'] = None
        elif is_reception:
            if source:
                self.add_error('source_location', "L'emplacement d'origine doit être vide pour un mouvement de réception.")
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

        if source and dest and source == dest:
            self.add_error('dest_location', "L'emplacement de destination doit être différent de l'emplacement d'origine.")
        return cleaned_data

class LineStockMoveForm(forms.ModelForm):
    class Meta:
        model = LineStockMove
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

