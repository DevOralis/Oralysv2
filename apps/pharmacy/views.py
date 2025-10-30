from django.shortcuts import render, redirect, get_object_or_404
from .models.pharmaceutical_form import PharmaceuticalForm
from .models.supplier import PharmacySupplier
from .models.dci import Dci
from .forms import PharmaceuticalFormForm, SupplierForm,DciForm
from .models.pharmacy import Pharmacy
from .models.location_type import PharmacyLocationType
from .forms import DciForm, PharmacyForm, LocationTypeForm, StockLocationForm
from .models.stock_location import PharmacyStockLocation
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models.pharmaceutical_form import PharmaceuticalForm
from .forms import PharmacyForm
from apps.purchases.models import Country, City, Language
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models.product import PharmacyProduct
from .models.product_location import PharmacyProductLocation
from .forms import ProductForm
import json
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models.functions import TruncMonth
from decimal import Decimal
from .models import PharmacyOrder, PharmacyOrderLine
from .forms import PharmacyOrderForm, PharmacyOrderLineForm
from apps.purchases.models import  Currency, Tax, PaymentMode
from django.forms import modelformset_factory
#-----------
from .forms import PharmacyStockMoveForm
from .models.pharmacy_stock_move import PharmacyStockMove
from .models.pharmacy_line_stock_move import PharmacyLineStockMove
from .models.pharmacy_operation_type import PharmacyOperationType
from .models.pharmacy_order import PharmacyOrder
from .models.pharmacy_order_line import PharmacyOrderLine
from apps.hr.models import Department
from django.db.models import Sum
try:
    from weasyprint import HTML, CSS
except Exception:
    HTML = None
    CSS = None
from .forms import OperationTypeForm
from .models.pharmacy_product_department import PharmacyProductDepartment
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.models import Max
from .forms import PharmacyProductCategoryForm, PharmacyUnitOfMesureForm
from .models.pharmacy_product_category import PharmacyProductCategory
from .models.pharmacy_product_uom import PharmacyUnitOfMesure
from django.db.models import Avg, Sum, Count
from apps.home.utils import log_action

def safe_decimal(val):
    """Convertit une valeur en Decimal de façon sécurisée"""
    try:
        if val is None or str(val).strip() == '':
            return Decimal('0')
        # Nettoie les caractères non-ASCII et espaces
        cleaned_val = str(val).replace('\xa0', '').replace(' ', '').strip()
        return Decimal(cleaned_val) if cleaned_val else Decimal('0')
    except (ValueError, TypeError, decimal.InvalidOperation):
        return Decimal('0')


def pharmaform_list(request):
    forms = PharmaceuticalForm.objects.all()
    return render(request, 'pharmaceuticalform_list.html', {'forms': forms, 'page_title': 'Liste Formes Galéniques'})

def pharmaform_create(request):
    form = PharmaceuticalFormForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        log_action(request.user, instance, 'creation')  # Log création
        return redirect('pharmaform_list')
    return render(request, 'pharmaceuticalform_form.html', {'form': form, 'page_title': 'Créer Forme Galénique'})

def pharmaform_update(request, pk):
    instance = get_object_or_404(PharmaceuticalForm, pk=pk)
    form = PharmaceuticalFormForm(request.POST or None, instance=instance)
    if form.is_valid():
        instance = form.save()
        log_action(request.user, instance, 'modification')  # Log modification
        return redirect('pharmaform_list')
    return render(request, 'pharmaceuticalform_form.html', {'form': form, 'page_title': 'Modifier Forme Galénique'})

@csrf_exempt
def pharmaform_delete(request, pk):
    instance = get_object_or_404(PharmaceuticalForm, pk=pk)
    if request.method == 'POST':
        log_action(request.user, instance, 'suppression')  # Log suppression
        instance.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def pharmacy_configuration(request):
    pharma_forms = PharmaceuticalForm.objects.all()
    dci_list = Dci.objects.all()
    pharmacy_list = Pharmacy.objects.all()
    location_types = PharmacyLocationType.objects.all()
    locations = PharmacyStockLocation.objects.select_related('parent_location', 'location_type')
    operation_types = PharmacyOperationType.objects.all()
    product_categories = PharmacyProductCategory.objects.all()
    product_units = PharmacyUnitOfMesure.objects.all()

    if request.method == 'POST':
        # Initialize all forms to ensure they are available in the context if validation fails
        form = PharmaceuticalFormForm()
        dci_form = DciForm()
        pharmacy_form = PharmacyForm()
        location_type_form = LocationTypeForm()
        location_form = StockLocationForm()
        operation_type_form = OperationTypeForm()
        product_category_form = PharmacyProductCategoryForm()
        product_unit_form = PharmacyUnitOfMesureForm()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            entity = request.POST.get('entity')
            action = request.POST.get('action')

            try:
                # pharmaform
                if entity == 'pharmaform':
                    if action == 'add':
                        form = PharmaceuticalFormForm(request.POST)
                        if form.is_valid():
                            instance = form.save()  # Sauvegarde d'abord
                            log_action(request.user, instance, 'creation')  # Log création après sauvegarde
                            return JsonResponse({'success': True})
                        return JsonResponse({'success': False, 'error': dict(form.errors)})

                    elif action == 'edit':
                        pk = request.POST.get('pk')
                        instance = get_object_or_404(PharmaceuticalForm, pk=pk)
                        form = PharmaceuticalFormForm(request.POST, instance=instance)
                        if form.is_valid():
                            instance = form.save()  # Sauvegarde d'abord
                            log_action(request.user, instance, 'modification')  # Log modification
                            return JsonResponse({'success': True})
                        return JsonResponse({'success': False, 'error': dict(form.errors)})

                    elif action == 'delete':
                        pk = request.POST.get('pk')
                        instance = get_object_or_404(PharmaceuticalForm, pk=pk)
                        from .models.product import PharmacyProduct
                        products_count = PharmacyProduct.objects.filter(pharmaceutical_form=instance).count()

                        if products_count > 0:
                            return JsonResponse({
                                'success': False,
                                'error': f'Cette forme galénique ne peut pas être supprimée car elle est utilisée dans {products_count} produit(s).'
                            })
                        log_action(request.user, instance, 'suppression')  # Log suppression
                        instance.delete()
                        return JsonResponse({'success': True})

                # dci
                elif entity == 'dci':
                    if action == 'add':
                        form = DciForm(request.POST)
                        if form.is_valid():
                            instance = form.save()  # Sauvegarde d'abord
                            log_action(request.user, instance, 'creation')  # Log création après sauvegarde
                            return JsonResponse({'success': True})
                        return JsonResponse({'success': False, 'error': dict(form.errors)})

                    elif action == 'edit':
                        pk = request.POST.get('pk')
                        instance = get_object_or_404(Dci, pk=pk)
                        form = DciForm(request.POST, instance=instance)
                        if form.is_valid():
                            instance = form.save()  # Sauvegarde d'abord
                            log_action(request.user, instance, 'modification')  # Log modification
                            return JsonResponse({'success': True})
                        return JsonResponse({'success': False, 'error': dict(form.errors)})

                    elif action == 'delete':
                        pk = request.POST.get('pk')
                        instance = get_object_or_404(Dci, pk=pk)
                        from .models.product import PharmacyProduct
                        products_count = PharmacyProduct.objects.filter(dci=instance).count()

                        if products_count > 0:
                            return JsonResponse({
                                'success': False,
                                'error': f'Cette DCI ne peut pas être supprimée car elle est utilisée dans {products_count} produit(s).'
                            })
                        log_action(request.user, instance, 'suppression')  # Log suppression
                        instance.delete()
                        return JsonResponse({'success': True})

                # pharmacy
                elif entity == 'pharmacy':
                    if action == 'add':
                        form = PharmacyForm(request.POST)
                        if form.is_valid():
                            instance = form.save()  # Sauvegarde d'abord
                            log_action(request.user, instance, 'creation')  # Log création après sauvegarde
                            return JsonResponse({'success': True})
                        return JsonResponse({'success': False, 'error': dict(form.errors)})

                    elif action == 'edit':
                        pk = request.POST.get('pk')
                        instance = get_object_or_404(Pharmacy, pk=pk)
                        form = PharmacyForm(request.POST, instance=instance)
                        if form.is_valid():
                            instance = form.save()  # Sauvegarde d'abord
                            log_action(request.user, instance, 'modification')  # Log modification
                            return JsonResponse({'success': True})
                        return JsonResponse({'success': False, 'error': dict(form.errors)})

                    elif action == 'delete':
                        pk = request.POST.get('pk')
                        instance = get_object_or_404(Pharmacy, pk=pk)
                        log_action(request.user, instance, 'suppression')  # Log suppression
                        instance.delete()
                        return JsonResponse({'success': True})

                # location_type
                elif entity == 'locationtype':
                    if action == 'add':
                        form = LocationTypeForm(request.POST)
                        if form.is_valid():
                            instance = form.save()  # Sauvegarde d'abord
                            log_action(request.user, instance, 'creation')  # Log création après sauvegarde
                            return JsonResponse({'success': True})
                        return JsonResponse({'success': False, 'error': dict(form.errors)})

                    elif action == 'edit':
                        pk = request.POST.get('pk')
                        instance = get_object_or_404(PharmacyLocationType, pk=pk)
                        form = LocationTypeForm(request.POST, instance=instance)
                        if form.is_valid():
                            instance = form.save()  # Sauvegarde d'abord
                            log_action(request.user, instance, 'modification')  # Log modification
                            return JsonResponse({'success': True})
                        return JsonResponse({'success': False, 'error': dict(form.errors)})

                    elif action == 'delete':
                        pk = request.POST.get('pk')
                        instance = get_object_or_404(PharmacyLocationType, pk=pk)
                        log_action(request.user, instance, 'suppression')  # Log suppression
                        instance.delete()
                        return JsonResponse({'success': True})

                # location
                elif entity == 'location':
                    if action == 'add':
                        form = StockLocationForm(request.POST)
                        if form.is_valid():
                            instance = form.save()  # Sauvegarde d'abord
                            log_action(request.user, instance, 'creation')  # Log création après sauvegarde
                            return JsonResponse({'success': True})
                        return JsonResponse({'success': False, 'error': dict(form.errors)})

                    elif action == 'edit':
                        pk = request.POST.get('pk')
                        instance = get_object_or_404(PharmacyStockLocation, pk=pk)
                        form = StockLocationForm(request.POST, instance=instance)
                        if form.is_valid():
                            instance = form.save()  # Sauvegarde d'abord
                            log_action(request.user, instance, 'modification')  # Log modification
                            return JsonResponse({'success': True})
                        return JsonResponse({'success': False, 'error': dict(form.errors)})

                    elif action == 'delete':
                        pk = request.POST.get('pk')
                        instance = get_object_or_404(PharmacyStockLocation, pk=pk)
                        log_action(request.user, instance, 'suppression')  # Log suppression
                        instance.delete()
                        return JsonResponse({'success': True})

                # operation_type
                elif entity == 'operationtype':
                    if action == 'add':
                        form = OperationTypeForm(request.POST)
                        if form.is_valid():
                            instance = form.save()  # Sauvegarde d'abord
                            log_action(request.user, instance, 'creation')  # Log création après sauvegarde
                            return JsonResponse({'success': True})
                        return JsonResponse({'success': False, 'error': dict(form.errors)})

                    elif action == 'edit':
                        pk = request.POST.get('pk')
                        instance = get_object_or_404(PharmacyOperationType, pk=pk)
                        form = OperationTypeForm(request.POST, instance=instance)
                        if form.is_valid():
                            instance = form.save()  # Sauvegarde d'abord
                            log_action(request.user, instance, 'modification')  # Log modification
                            return JsonResponse({'success': True})
                        return JsonResponse({'success': False, 'error': dict(form.errors)})

                    elif action == 'delete':
                        pk = request.POST.get('pk')
                        instance = get_object_or_404(PharmacyOperationType, pk=pk)
                        log_action(request.user, instance, 'suppression')  # Log suppression
                        instance.delete()
                        return JsonResponse({'success': True})

                # category
                elif entity == 'category':
                    if action == 'add':
                        form = PharmacyProductCategoryForm(request.POST)
                        if form.is_valid():
                            instance = form.save()  # Sauvegarde d'abord
                            log_action(request.user, instance, 'creation')  # Log création après sauvegarde
                            return JsonResponse({'success': True})
                        return JsonResponse({'success': False, 'error': dict(form.errors)})

                    elif action == 'edit':
                        pk = request.POST.get('pk')
                        instance = get_object_or_404(PharmacyProductCategory, pk=pk)
                        form = PharmacyProductCategoryForm(request.POST, instance=instance)
                        if form.is_valid():
                            instance = form.save()  # Sauvegarde d'abord
                            log_action(request.user, instance, 'modification')  # Log modification
                            return JsonResponse({'success': True})
                        return JsonResponse({'success': False, 'error': dict(form.errors)})

                    elif action == 'delete':
                        pk = request.POST.get('pk')
                        instance = get_object_or_404(PharmacyProductCategory, pk=pk)
                        log_action(request.user, instance, 'suppression')  # Log suppression
                        instance.delete()
                        return JsonResponse({'success': True})

                # unit
                elif entity == 'unit':
                    if action == 'add':
                        form = PharmacyUnitOfMesureForm(request.POST)
                        if form.is_valid():
                            instance = form.save()  # Sauvegarde d'abord
                            log_action(request.user, instance, 'creation')  # Log création après sauvegarde
                            return JsonResponse({'success': True})
                        return JsonResponse({'success': False, 'error': dict(form.errors)})

                    elif action == 'edit':
                        pk = request.POST.get('pk')
                        instance = get_object_or_404(PharmacyUnitOfMesure, pk=pk)
                        form = PharmacyUnitOfMesureForm(request.POST, instance=instance)
                        if form.is_valid():
                            instance = form.save()  # Sauvegarde d'abord
                            log_action(request.user, instance, 'modification')  # Log modification
                            return JsonResponse({'success': True})
                        return JsonResponse({'success': False, 'error': dict(form.errors)})

                    elif action == 'delete':
                        pk = request.POST.get('pk')
                        instance = get_object_or_404(PharmacyUnitOfMesure, pk=pk)
                        log_action(request.user, instance, 'suppression')  # Log suppression
                        instance.delete()
                        return JsonResponse({'success': True})

                else:
                    return JsonResponse({'success': False, 'error': 'Entité non reconnue'})

            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})

        # Regular POST submissions
        elif 'form_submit' in request.POST:
            form_id = request.POST.get('form_id', '').strip()
            instance = get_object_or_404(PharmaceuticalForm, pk=form_id) if form_id else None
            form = PharmaceuticalFormForm(request.POST, instance=instance)
            if form.is_valid():
                instance = form.save()
                log_action(request.user, instance, 'creation' if not form_id else 'modification')  # Log création ou modification
                return redirect('/pharmacy/configuration?success=1')

        elif 'dci_submit' in request.POST:
            dci_id = request.POST.get('dci_id', '').strip()
            instance = get_object_or_404(Dci, pk=dci_id) if dci_id else None
            dci_form = DciForm(request.POST, instance=instance)
            if dci_form.is_valid():
                instance = dci_form.save()
                log_action(request.user, instance, 'creation' if not dci_id else 'modification')  # Log création ou modification
                return redirect('/pharmacy/configuration?dci_success=1')

        elif 'pharmacy_submit' in request.POST:
            pharmacy_id = request.POST.get('pharmacy_id', '').strip()
            instance = get_object_or_404(Pharmacy, pk=pharmacy_id) if pharmacy_id else None
            pharmacy_form = PharmacyForm(request.POST, instance=instance)
            if pharmacy_form.is_valid():
                instance = pharmacy_form.save()
                log_action(request.user, instance, 'creation' if not pharmacy_id else 'modification')  # Log création ou modification
                return redirect('/pharmacy/configuration?pharmacy_success=1')

        elif 'location_type_submit' in request.POST:
            location_type_id = request.POST.get('location_type_id', '').strip()
            instance = get_object_or_404(PharmacyLocationType, pk=location_type_id) if location_type_id else None
            location_type_form = LocationTypeForm(request.POST, instance=instance)
            if location_type_form.is_valid():
                instance = location_type_form.save()
                log_action(request.user, instance, 'creation' if not location_type_id else 'modification')  # Log création ou modification
                return redirect('/pharmacy/configuration?location_type_success=1')

        elif 'location_submit' in request.POST:
            location_id = request.POST.get('location_id', '').strip()
            instance = get_object_or_404(PharmacyStockLocation, pk=location_id) if location_id else None
            location_form = StockLocationForm(request.POST, instance=instance)
            if location_form.is_valid():
                instance = location_form.save()
                log_action(request.user, instance, 'creation' if not location_id else 'modification')  # Log création ou modification
                return redirect('/pharmacy/configuration?location_success=1')

        elif 'operation_type_submit' in request.POST:
            operation_type_id = request.POST.get('operation_type_id', '').strip()
            instance = get_object_or_404(PharmacyOperationType, pk=operation_type_id) if operation_type_id else None
            operation_type_form = OperationTypeForm(request.POST, instance=instance)
            if operation_type_form.is_valid():
                instance = operation_type_form.save()
                log_action(request.user, instance, 'creation' if not operation_type_id else 'modification')  # Log création ou modification
                return redirect('/pharmacy/configuration?operation_type_success=1')

        elif 'category_submit' in request.POST:
            category_id = request.POST.get('category_id', '').strip()
            instance = get_object_or_404(PharmacyProductCategory, pk=category_id) if category_id else None
            product_category_form = PharmacyProductCategoryForm(request.POST, instance=instance)
            if product_category_form.is_valid():
                instance = product_category_form.save()
                log_action(request.user, instance, 'creation' if not category_id else 'modification')  # Log création ou modification
                return redirect('/pharmacy/configuration?category_success=1')

        elif 'unit_submit' in request.POST:
            unit_id = request.POST.get('unit_id', '').strip()
            instance = get_object_or_404(PharmacyUnitOfMesure, pk=unit_id) if unit_id else None
            product_unit_form = PharmacyUnitOfMesureForm(request.POST, instance=instance)
            if product_unit_form.is_valid():
                instance = product_unit_form.save()
                log_action(request.user, instance, 'creation' if not unit_id else 'modification')  # Log création ou modification
                return redirect('/pharmacy/configuration?unit_success=1')

    else:
        form = PharmaceuticalFormForm()
        dci_form = DciForm()
        pharmacy_form = PharmacyForm()
        location_type_form = LocationTypeForm()
        location_form = StockLocationForm()
        operation_type_form = OperationTypeForm()
        product_category_form = PharmacyProductCategoryForm()
        product_unit_form = PharmacyUnitOfMesureForm()

    return render(request, 'pharmacy_configuration.html', {
        'pharma_forms': pharma_forms,
        'form': form,
        'dci_list': dci_list,
        'dci_form': dci_form,
        'pharmacy_list': pharmacy_list,
        'pharmacy_form': pharmacy_form,
        'location_types': location_types,
        'location_type_form': location_type_form,
        'locations': locations,
        'location_form': location_form,
        'operation_types': operation_types,
        'operation_type_form': operation_type_form,
        'product_categories': product_categories,
        'product_category_form': product_category_form,
        'product_units': product_units,
        'product_unit_form': product_unit_form,
        'page_title': 'Configuration Pharmacie',
    })

# Vue pour la suppression des pharmacies
@csrf_exempt
def pharmacy_delete(request, pk):
    instance = get_object_or_404(Pharmacy, pk=pk)
    if request.method == 'POST':
        try:
            log_action(request.user, instance, 'suppression')  # Log suppression
            instance.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

# -----------
# Supplier
# -----------

def supplier_list(request):
    # Base queryset
    suppliers_query = PharmacySupplier.objects.all().order_by('name')

    # Search and filter
    query = request.GET.get('q')
    city_id = request.GET.get('city')

    if query:
        suppliers_query = suppliers_query.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )

    if city_id:
        suppliers_query = suppliers_query.filter(city_id=city_id)

    # Add pagination with 5 items per page
    paginator = Paginator(suppliers_query, 5)
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(1)

    # Handle AJAX request for search/filter
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        context = {'suppliers': page_obj, 'request': request}
        html = render_to_string('_suppliers_table.html', context)
        
        # Include pagination data for AJAX response
        pagination_data = {
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'page_range': list(paginator.page_range),
        }
        
        return JsonResponse({
            'html': html,
            'pagination': pagination_data
        })

    # Handle full page load (non-AJAX)
    form = SupplierForm()
    countries = Country.objects.all()
    cities = City.objects.all()
    languages = Language.objects.all()
    
    # Handle edit mode
    supplier_instance = None
    if 'edit' in request.GET:
        supplier_id = request.GET.get('edit')
        if supplier_id:
            supplier_instance = get_object_or_404(PharmacySupplier, pk=supplier_id)
            form = SupplierForm(instance=supplier_instance)
    
    import json
    
    pagination_data = {
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'page_range': list(paginator.page_range),
    }
    
    context = {
        'suppliers': page_obj,
        'form': form,
        'countries': countries,
        'cities': cities,
        'languages': languages,
        'supplier': supplier_instance,
        'page_title': 'Fournisseurs',
        'pagination': json.dumps(pagination_data),
    }
    return render(request, 'suppliers.html', context)

def supplier_create(request):
    if request.method == 'POST':
        try:
            form = SupplierForm(request.POST, request.FILES)
            if form.is_valid():
                supplier = form.save()
                log_action(request.user, supplier, 'creation')  # Log création
                supplier_data = {
                    'id': supplier.pk,
                    'name': supplier.name,
                    'email': supplier.email or '',
                    'phone': supplier.phone or '',
                    'street': supplier.street or '',
                    'street2': supplier.street2 or '',
                    'city': {'name': supplier.city.name} if supplier.city else None,
                    'country': {'name': supplier.country.name} if supplier.country else None,
                    'logo': supplier.logo.url if supplier.logo else None,
                }
                return JsonResponse({
                    'status': 'success',
                    'message': 'Fournisseur créé avec succès',
                    'supplier': supplier_data
                })
            else:
                errors = {field: [str(error) for error in field_errors] for field, field_errors in form.errors.items()}
                return JsonResponse({
                    'status': 'error',
                    'message': 'Erreurs de validation',
                    'errors': errors
                }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Erreur serveur: {str(e)}'
            }, status=500)
    return redirect('pharmacy_supplier_list')


def supplier_update(request, pk):
    supplier = get_object_or_404(PharmacySupplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, request.FILES, instance=supplier)
        if form.is_valid():
            supplier = form.save()
            log_action(request.user, supplier, 'modification')  # Log modification
            supplier_data = {
                'id': supplier.pk,
                'name': supplier.name,
                'email': supplier.email or '',
                'phone': supplier.phone or '',
                'street': supplier.street or '',
                'street2': supplier.street2 or '',
                'city': {'name': supplier.city.name} if supplier.city else None,
                'country': {'name': supplier.country.name} if supplier.country else None,
                'logo': supplier.logo.url if supplier.logo else None,
            }
            return JsonResponse({
                'status': 'success',
                'message': 'Fournisseur modifié avec succès',
                'supplier': supplier_data
            })
        else:
            errors = {field: [str(error) for error in field_errors] for field, field_errors in form.errors.items()}
            return JsonResponse({
                'status': 'error',
                'message': 'Erreurs de validation',
                'errors': errors
            }, status=400)
    else:
        form = SupplierForm(instance=supplier)
        countries = Country.objects.all()
        cities = City.objects.all()
        languages = Language.objects.all()
        suppliers = PharmacySupplier.objects.all()
        return render(request, 'suppliers.html', {
            'form': form,
            'supplier': supplier,
            'countries': countries,
            'cities': cities,
            'languages': languages,
            'suppliers': suppliers,
            'page_title': 'Modifier Fournisseur',
        })

@csrf_exempt
@require_POST
def supplier_delete(request, pk):
    try:
        instance = get_object_or_404(PharmacySupplier, pk=pk)
        supplier_name = instance.name
        log_action(request.user, instance, 'suppression')  # Log suppression
        instance.delete()
        return JsonResponse({
            'status': 'success',
            'message': f'Fournisseur "{supplier_name}" supprimé avec succès'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Erreur lors de la suppression: {str(e)}'
        }, status=500)
   
# -------------------
# DCI
# -------------------

@csrf_protect
def dci_list(request):
    dcis = Dci.objects.all()
    return render(request, 'dci_list.html', {'dcis': dcis, 'page_title': 'Liste DCI'})

@csrf_protect
def dci_create(request):
    form = DciForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        log_action(request.user, instance, 'creation')  # Log création
        messages.success(request, 'DCI ajoutée avec succès.')
        return redirect('dci_list')
    return render(request, 'dci_form.html', {'form': form, 'page_title': 'Créer DCI'})

@csrf_protect
def dci_update(request, pk):
    instance = get_object_or_404(Dci, pk=pk)
    form = DciForm(request.POST or None, instance=instance)
    if form.is_valid():
        instance = form.save()
        log_action(request.user, instance, 'modification')  # Log modification
        messages.success(request, 'DCI modifiée avec succès.')
        return redirect('dci_list')
    return render(request, 'dci_form.html', {'form': form, 'page_title': 'Modifier DCI'})

@csrf_exempt
def dci_delete(request, pk):
    instance = get_object_or_404(Dci, pk=pk)
    if request.method == 'POST':
        log_action(request.user, instance, 'suppression')  # Log suppression
        instance.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


# -------------------
# PHARMACY
# -------------------

@csrf_protect
def pharmacy_list(request):
    pharmacies = Pharmacy.objects.all()
    return render(request, 'pharmacy_list.html', {'pharmacies': pharmacies, 'page_title': 'Liste Pharmacies'})

@csrf_protect
def pharmacy_create(request):
    form = PharmacyForm(request.POST or None)
    if form.is_valid():
        instance = form.save()
        log_action(request.user, instance, 'creation')  # Log création
        messages.success(request, 'Pharmacie ajoutée avec succès.')
        return redirect('pharmacy_list')
    return render(request, 'pharmacy_form.html', {'form': form, 'page_title': 'Créer Pharmacie'})

@csrf_protect
def pharmacy_update(request, pk):
    instance = get_object_or_404(Pharmacy, pk=pk)
    form = PharmacyForm(request.POST or None, instance=instance)
    if form.is_valid():
        instance = form.save()
        log_action(request.user, instance, 'modification')  # Log modification
        messages.success(request, 'Pharmacie modifiée avec succès.')
        return redirect('pharmacy_list')
    return render(request, 'pharmacy_form.html', {'form': form, 'page_title': 'Modifier Pharmacie'})

@csrf_protect
def pharmacy_delete(request, pk):
    instance = get_object_or_404(Pharmacy, pk=pk)
    if request.method == 'POST':
        log_action(request.user, instance, 'suppression')  # Log suppression
        instance.delete()
        messages.success(request, 'Pharmacie supprimée avec succès.')
        return redirect('pharmacy_list')
    return render(request, 'pharmacy_confirm_delete.html', {'pharmacy': instance, 'page_title': 'Supprimer Pharmacie'})

# ------------------------- PHARMACY Config--------------
@require_POST
@csrf_exempt
def location_type_delete(request, pk):
    try:
        location_type = PharmacyLocationType.objects.get(pk=pk)
        log_action(request.user, location_type, 'suppression')  # Log suppression
        location_type.delete()
        return JsonResponse({'success': True})
    except PharmacyLocationType.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Type Location introuvable'})
@csrf_exempt
@require_POST
def stock_location_delete(request, pk):
    try:
        location = get_object_or_404(PharmacyStockLocation, pk=pk)
        log_action(request.user, location, 'suppression')  # Log suppression
        location.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
@csrf_exempt
@require_POST
def delete_pharmacy(request, pk):
    try:
        pharmacy = get_object_or_404(Pharmacy, pk=pk)
        log_action(request.user, pharmacy, 'suppression')  # Log suppression
        pharmacy.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
#-----------operation type delete ---
@require_POST
@csrf_exempt
def operation_type_delete(request, pk):
    try:
        operation_type = PharmacyOperationType.objects.get(pk=pk)
        log_action(request.user, operation_type, 'suppression')  # Log suppression
        operation_type.delete()
        return JsonResponse({'success': True})
    except PharmacyOperationType.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Type Operation introuvable'})

# ------------Category delete--------------------------------
@csrf_exempt
@require_POST
def product_category_delete(request, pk):
    try:
        category = PharmacyProductCategory.objects.get(pk=pk)
        log_action(request.user, category, 'suppression')  # Log suppression
        category.delete()
        return JsonResponse({'success': True})
    except PharmacyProductCategory.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Catégorie de produit introuvable'})
# ------------Unit of measure delete--------------------------------
@csrf_exempt
@require_POST
def product_unit_delete(request, pk):
    try:
        unit = PharmacyUnitOfMesure.objects.get(pk=pk)
        log_action(request.user, unit, 'suppression')  # Log suppression
        unit.delete()
        return JsonResponse({'success': True})
    except PharmacyUnitOfMesure.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Unité de mesure introuvable'})

def pharmacy_product_list(request):
    """Vue pour afficher la liste des produits pharmaceutiques avec filtres et pagination."""
    try:
        # Récupérer les paramètres de requête
        query = request.GET.get('q', '').strip()
        pharmaceutical_form_filter = request.GET.get('pharmaceutical_form', '').strip()
        sort_by = request.GET.get('sort_by', 'product_id')
        sort_order = request.GET.get('sort_order', 'desc')
        page_number = request.GET.get('page', '1')
        
        # Requête de base avec les relations nécessaires
        products = PharmacyProduct.objects.select_related(
            'pharmaceutical_form',
            'dci'
        )
        
        # Filtrer par forme pharmaceutique si spécifié
        if pharmaceutical_form_filter:
            try:
                # Validation du filtre
                if pharmaceutical_form_filter.isdigit():
                    products = products.filter(pharmaceutical_form_id=pharmaceutical_form_filter)
                else:
                    products = products.filter(pharmaceutical_form__name__iexact=pharmaceutical_form_filter)
            except Exception as e:
                request.session['swal_error'] = f"Erreur lors du filtrage par forme pharmaceutique : {str(e)}"
        
        # Appliquer la recherche si spécifiée
        if query:
            # Normaliser la requête pour gérer les séparateurs décimaux
            normalized_query = query.replace(',', '.')
            
            products = products.filter(
                Q(code__icontains=query) |
                Q(short_label__icontains=query) |
                Q(brand__icontains=query) |
                Q(full_label__icontains=query) |
                Q(dci__label__icontains=query) |
                Q(pharmaceutical_form__name__icontains=query) |
                Q(dosage__icontains=query) |
                Q(unit_price__icontains=normalized_query) |
                Q(total_quantity_cached__icontains=normalized_query) |
                Q(barcode__icontains=query)
            ).distinct()
        
        # Apply sorting mapping similar to inventory
        sort_mapping = {
            'code': 'code',
            'short_label': 'short_label',
            'brand': 'brand',
            'dci': 'dci__label',
            'pharmaceutical_form': 'pharmaceutical_form__name',
            'unit_price': 'unit_price',
            'total_quantity_cached': 'total_quantity_cached',
            'product_id': 'product_id',
        }
        sort_field = sort_mapping.get(sort_by, 'product_id')
        order_prefix = '-' if sort_order == 'desc' else ''
        products = products.order_by(f'{order_prefix}{sort_field}')

        
        

        # Pagination
        paginator = Paginator(products, 15)  # 15 éléments par page
        
        try:
            if not page_number.isdigit():
                page_number = '1'
            page_obj = paginator.page(page_number)
        except Exception:
            page_obj = paginator.page(1)
        
        # Préparer le contexte
        context = {
            'page_obj': page_obj,
            'sort_by': sort_by,
            'sort_order': sort_order,
            'form': ProductForm(),
            'page_title': 'Produits Pharmaceutiques',
            'product': None,
            'locations': PharmacyStockLocation.objects.select_related('location_type', 'parent_location').all(),
            'pharmaceutical_forms': PharmaceuticalForm.objects.all().order_by('name'),
            'search': query,
            'current_pharmaceutical_form': pharmaceutical_form_filter,
            'total_products': products.count(),
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
        }
        
        # Ajouter les informations de localisation des produits
        product_locations_json = {}
        for product in page_obj:
            locations = list(PharmacyProductLocation.objects.filter(product=product)
                           .values('location_id', 'quantity_stored'))
            for loc in locations:
                loc['quantity_stored'] = float(loc['quantity_stored'])
            product_locations_json[product.pk] = json.dumps(locations)
        context['product_locations_json'] = product_locations_json
        
        # Gérer les messages de session
        context['swal_success'] = request.session.pop('swal_success', None)
        context['swal_error'] = request.session.pop('swal_error', None)
        
        # Retourner la réponse appropriée selon le type de requête
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, 'product_table_body.html', context)
        return render(request, 'productsList.html', context)
        
    except Exception as e:
        # Gérer les erreurs générales
        message = f"Une erreur est survenue lors du chargement de la liste des produits : {str(e)}"
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': message}, status=500)
        request.session['swal_error'] = message
        return redirect('pharmacy_product_list')

def generate_product_code():
    last_product = PharmacyProduct.objects.filter(code__startswith='PHPDT-').order_by('-product_id').first()
    if last_product and last_product.code:
        try:
            last_number = int(last_product.code.split('-')[-1])
        except ValueError:
            last_number = 0
    else:
        last_number = 0
    return f'PHPDT-{last_number + 1:04d}'

@csrf_exempt
@transaction.atomic
def pharmacy_product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.code = generate_product_code()
            product.save()
            log_action(request.user, product, 'creation')
            PharmacyProductLocation.objects.filter(product=product).delete()
            locations_json = request.POST.get('locations_json', '[]')
            try:
                locations = json.loads(locations_json)
            except json.JSONDecodeError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Erreur dans les données des emplacements.'
                }, status=400)
            total = 0
            for loc in locations:
                location_id = loc.get('location_id')
                quantity_stored = loc.get('quantity_stored')
                if location_id and quantity_stored:
                    try:
                        location = PharmacyStockLocation.objects.get(pk=location_id)
                        quantity = float(quantity_stored)
                        if quantity < 0:
                            raise ValueError("La quantité ne peut pas être négative.")
                        PharmacyProductLocation.objects.create(
                            product=product,
                            location=location,
                            quantity_stored=quantity,
                            last_count_date=timezone.now().date()
                        )
                        total += quantity
                    except (PharmacyStockLocation.DoesNotExist, ValueError) as e:
                        return JsonResponse({
                            'status': 'error',
                            'message': f"Emplacement {location_id} invalide ou quantité incorrecte: {str(e)}"
                        }, status=400)
            product.total_quantity_cached = total
            product.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Produit créé avec succès !'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Erreur dans le formulaire produit.',
                'errors': form.errors.as_json()
            }, status=400)
    else:
        form = ProductForm()
        products = PharmacyProduct.objects.all().order_by('-product_id')
        paginator = Paginator(products, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        product_locations_json = {}
        for product in page_obj:
            product_locations = list(PharmacyProductLocation.objects.filter(product=product).values('location_id', 'quantity_stored'))
            for loc in product_locations:
                loc['quantity_stored'] = float(loc['quantity_stored'])
            product_locations_json[product.pk] = json.dumps(product_locations)
        return render(request, 'productsList.html', {
            'form': form,
            'page_title': 'Ajouter un Produit Pharmaceutique',
            'product': None,
            'locations': PharmacyStockLocation.objects.all(),
            'product_locations': json.dumps([]),
            'product_locations_json': product_locations_json,
            'products': products,
            'page_obj': page_obj,
            'pharmaceutical_forms': PharmaceuticalForm.objects.all().order_by('name'),
            'search': request.GET.get('q', ''),
            'current_pharmaceutical_form': request.GET.get('pharmaceutical_form', ''),
            'total_products': products.count(),
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
        })

@csrf_exempt
@transaction.atomic
def pharmacy_product_update(request, pk):
    try:
        product = get_object_or_404(PharmacyProduct, pk=pk)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Produit avec ID {pk} non trouvé.'
        }, status=404)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            log_action(request.user, product, 'modification')
            PharmacyProductLocation.objects.filter(product=product).delete()
            locations_json = request.POST.get('locations_json', '[]')
            try:
                locations = json.loads(locations_json)
            except json.JSONDecodeError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Erreur dans les données des emplacements.'
                }, status=400)
            total = 0
            for loc in locations:
                location_id = loc.get('location_id')
                quantity_stored = loc.get('quantity_stored')
                if location_id and quantity_stored:
                    try:
                        location = PharmacyStockLocation.objects.get(pk=location_id)
                        quantity = float(quantity_stored)
                        if quantity < 0:
                            raise ValueError("La quantité ne peut pas être négative.")
                        PharmacyProductLocation.objects.create(
                            product=product,
                            location=location,
                            quantity_stored=quantity,
                            last_count_date=timezone.now().date()
                        )
                        total += quantity
                    except (PharmacyStockLocation.DoesNotExist, ValueError) as e:
                        return JsonResponse({
                            'status': 'error',
                            'message': f"Emplacement {location_id} invalide ou quantité incorrecte: {str(e)}"
                        }, status=400)
            product.total_quantity_cached = total
            product.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Produit modifié avec succès !'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Erreur dans le formulaire produit.',
                'errors': form.errors.as_json()
            }, status=400)
    else:
        form = ProductForm(instance=product)
        product_locations = list(PharmacyProductLocation.objects.filter(product=product).values('location_id', 'quantity_stored'))
        for loc in product_locations:
            loc['quantity_stored'] = float(loc['quantity_stored'])
        product_locations_json = json.dumps(product_locations) if product_locations else json.dumps([])
        products = PharmacyProduct.objects.all().order_by('-product_id')
        product_locations_dict = {}
        for p in products:
            locs = list(PharmacyProductLocation.objects.filter(product=p).values('location_id', 'quantity_stored'))
            for loc in locs:
                loc['quantity_stored'] = float(loc['quantity_stored'])
            product_locations_dict[p.pk] = json.dumps(locs)
        paginator = Paginator(products, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'productsList.html', {
            'form': form,
            'page_title': 'Modifier un Produit Pharmaceutique',
            'product': product,
            'locations': PharmacyStockLocation.objects.all(),
            'product_locations': product_locations_json,
            'products': products,
            'page_obj': paginator.get_page(page_number),
            'product_locations_json': product_locations_dict,
            'pharmaceutical_forms': PharmaceuticalForm.objects.all().order_by('name'),
            'search': request.GET.get('q', ''),
            'current_pharmaceutical_form': request.GET.get('pharmaceutical_form', ''),
            'total_products': products.count(),
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
        })

@csrf_exempt
def pharmacy_product_delete(request, pk):
    try:
        product = get_object_or_404(PharmacyProduct, pk=pk)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'title': 'Erreur',
            'message': f'Produit avec ID {pk} non trouvé.'
        }, json_dumps_params={'ensure_ascii': False})
    if request.method == 'POST':
        try:
            stock_moves = PharmacyStockMove.objects.filter(lines__product=product).exists()
            if stock_moves:
                return JsonResponse({
                    'status': 'error',
                    'title': 'Suppression impossible',
                    'message': 'Ce produit est utilisé dans des mouvements de stock et ne peut pas être supprimé.'
                }, json_dumps_params={'ensure_ascii': False})

            orders = PharmacyOrderLine.objects.filter(product=product).exists()
            if orders:
                return JsonResponse({
                    'status': 'error',
                    'title': 'Suppression impossible',
                    'message': 'Ce produit est utilisé dans des commandes et ne peut pas être supprimé.'
                }, json_dumps_params={'ensure_ascii': False})

            log_action(request.user, product, 'suppression')  # Log suppression
            product.delete()
            return JsonResponse({
                'status': 'success',
                'title': 'Succès',
                'message': 'Le produit a été supprimé avec succès.'
            }, json_dumps_params={'ensure_ascii': False})

        except Exception as e:
            import traceback
            print(f"Error deleting product {pk}: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({
                'status': 'error',
                'title': 'Erreur',
                'message': f'Une erreur est survenue lors de la suppression : {str(e)}'
            }, json_dumps_params={'ensure_ascii': False})

    return render(request, 'productsList.html', {
        'object': product,
        'page_title': 'Supprimer Produit Pharmaceutique',
        'cancel_url': 'pharmacy_product_list',
    })
def pharmacy_product_list_ajax(request):
    query = request.GET.get('q', '')
    pharmaceutical_form = request.GET.get('pharmaceutical_form', '')
    
    products = PharmacyProduct.objects.all().order_by('-product_id')
    
    # Appliquer le filtre par forme pharmaceutique
    if pharmaceutical_form:
        products = products.filter(pharmaceutical_form_id=pharmaceutical_form)
    
    # Appliquer le filtre de recherche
    if query:
        products = products.filter(
            Q(code__icontains=query) |
            Q(short_label__icontains=query) |
            Q(brand__icontains=query) |
            Q(full_label__icontains=query) |
            Q(dci__label__icontains=query) |
            Q(pharmaceutical_form__name__icontains=query) |
            Q(barcode__icontains=query)
        )
    
    # Pagination avec 5 éléments par page
    paginator = Paginator(products, 5)
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.get_page(page_number)
    except Exception:
        page_obj = paginator.page(1)
    
    # Préparer les données des emplacements pour chaque produit
    product_locations_json = {}
    for product in page_obj:
        product_locations = list(PharmacyProductLocation.objects.filter(product=product).values('location_id', 'quantity_stored'))
        for loc in product_locations:
            loc['quantity_stored'] = float(loc['quantity_stored'])
        product_locations_json[product.pk] = json.dumps(product_locations)
    
    return render(request, 'product_table_body.html', {
                'page_obj': page_obj,
                'product_locations_json': product_locations_json,
        'search': query,
        'current_pharmaceutical_form': pharmaceutical_form,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
                'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
    })

def pharmacy_order_list(request):
    orders = PharmacyOrder.objects.all().select_related('supplier')
    suppliers = PharmacySupplier.objects.all()
    products = PharmacyProduct.objects.all()
    currencies = Currency.objects.all()
    taxes = Tax.objects.all()
    payment_modes = PaymentMode.objects.all()
    # Récupérer et nettoyer les messages SweetAlert stockés en session
    swal_success = request.session.pop('swal_success', None)
    swal_error = request.session.pop('swal_error', None)

    context = {
        'orders': orders,
        'suppliers': suppliers,
        'products': products,
        'currencies': currencies,
        'taxes': taxes,
        'payment_modes': payment_modes,
        'page_title': 'Commandes Pharmacie',
        'swal_success': swal_success,
        'swal_error': swal_error,
    }

    return render(request, 'pharmacy_orders.html', context)

@transaction.atomic
def create_pharmacy_order(request):
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier')
        date_order = request.POST.get('order_date')
        currency_id = request.POST.get('currency')
        payment_mode_id = request.POST.get('payment_mode')

        if not all([supplier_id, date_order, currency_id]):
            messages.error(request, 'Veuillez remplir tous les champs obligatoires: Fournisseur, Date de commande, Devise.')
            return render(request, 'new_pharmacy_order.html', {
                'products': PharmacyProduct.objects.all(),
                'suppliers': PharmacySupplier.objects.all(),
                'currencies': Currency.objects.all(),
                'taxes': Tax.objects.all(),
                'payment_modes': PaymentMode.objects.all(),
                'page_title': 'Nouvelle Commande Pharmacie',
                'reference': request.POST.get('reference', ''),
            })

        last_order = PharmacyOrder.objects.order_by('-id').first()
        next_id = (last_order.id + 1) if last_order else 1
        reference = f'PHARM-PR-{next_id:06d}'

        try:
            supplier = get_object_or_404(PharmacySupplier, pk=supplier_id)
            currency = get_object_or_404(Currency, pk=currency_id)
            payment_mode = get_object_or_404(PaymentMode, pk=payment_mode_id) if payment_mode_id else None
        except Exception as e:
            messages.error(request, f'Erreur lors de la récupération des données: {str(e)}')
            return render(request, 'new_pharmacy_order.html', {
                'products': PharmacyProduct.objects.all(),
                'suppliers': PharmacySupplier.objects.all(),
                'currencies': Currency.objects.all(),
                'taxes': Tax.objects.all(),
                'payment_modes': PaymentMode.objects.all(),
                'page_title': 'Nouvelle Commande Pharmacie',
                'reference': reference,
            })

        order = PharmacyOrder.objects.create(
            name=reference,
            supplier=supplier,
            date_order=date_order,
            currency=currency,
            payment_mode=payment_mode,
            amount_untaxed=Decimal('0.00'),
            amount_tax=Decimal('0.00'),
            amount_total=Decimal('0.00'),
            invoice_status='to_invoice',
            date_planned=timezone.now(),
            notes=request.POST.get('notes', ''),
        )
        log_action(request.user, order, 'creation')  # Log création

        products = request.POST.getlist('product[]')
        quantities = request.POST.getlist('quantity[]')
        unit_prices = request.POST.getlist('unit_price[]')
        taxes = request.POST.getlist('tax[]')

        if not products or not quantities or not unit_prices:
            messages.error(request, 'Au moins une ligne de commande avec produit, quantité et prix unitaire est requise.')
            order.delete()
            return render(request, 'new_pharmacy_order.html', {
                'products': PharmacyProduct.objects.all(),
                'suppliers': PharmacySupplier.objects.all(),
                'currencies': Currency.objects.all(),
                'taxes': Tax.objects.all(),
                'payment_modes': PaymentMode.objects.all(),
                'page_title': 'Nouvelle Commande Pharmacie',
                'reference': reference,
            })

        valid_lines = False
        for i in range(len(products)):
            product_name = products[i].strip()
            if not product_name:
                continue
            product = PharmacyProduct.objects.filter(short_label__exact=product_name).first()
            if not product:
                messages.warning(request, f'Produit "{product_name}" non trouvé.')
                continue
            try:
                qty = Decimal(quantities[i])
                price_unit = Decimal(unit_prices[i])
                if qty <= 0 or price_unit < 0:
                    messages.warning(request, f'Quantité ou prix unitaire invalide pour "{product_name}".')
                    continue
                subtotal = qty * price_unit
                tax_id = taxes[i] if i < len(taxes) and taxes[i] else None
                tax = Tax.objects.get(pk=tax_id) if tax_id else None

                PharmacyOrderLine.objects.create(
                    order=order,
                    product=product,
                    product_qty=float(qty),
                    price_unit=price_unit,
                    price_subtotal=subtotal,
                    tax=tax,
                    name=product.short_label,
                )

                tax_amount = Decimal('0.00')
                if tax and hasattr(tax, 'valeur'):
                    tax_amount = subtotal * (Decimal(str(tax.valeur)) / Decimal('100.0'))

                order.amount_untaxed += subtotal
                order.amount_tax += tax_amount
                valid_lines = True
            except (ValueError, Tax.DoesNotExist) as e:
                messages.warning(request, f'Erreur pour la ligne "{product_name}": {str(e)}')
                continue

        if not valid_lines:
            messages.error(request, 'Aucune ligne de commande valide n\'a été créée.')
            order.delete()
            return render(request, 'new_pharmacy_order.html', {
                'products': PharmacyProduct.objects.all(),
                'suppliers': PharmacySupplier.objects.all(),
                'currencies': Currency.objects.all(),
                'taxes': Tax.objects.all(),
                'payment_modes': PaymentMode.objects.all(),
                'page_title': 'Nouvelle Commande Pharmacie',
                'reference': reference,
            })

        order.amount_total = order.amount_untaxed + order.amount_tax
        order.save()

        request.session['swal_success'] = 'Commande créée avec succès.'
        # Si la requête est AJAX, renvoyer l'URL de redirection en JSON pour éviter la redirection côté fetch
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'redirect_url': reverse('pharmacy_order_list'), 'success': True})
        return redirect('pharmacy_order_list')

    last_order = PharmacyOrder.objects.order_by('-id').first()
    next_id = (last_order.id + 1) if last_order else 1
    reference = f'PHARM-PR-{next_id:06d}'

    return render(request, 'new_pharmacy_order.html', {
        'products': PharmacyProduct.objects.all(),
        'suppliers': PharmacySupplier.objects.all(),
        'currencies': Currency.objects.all(),
        'taxes': Tax.objects.all(),
        'payment_modes': PaymentMode.objects.all(),
        'page_title': 'Nouvelle Commande Pharmacie',
        'reference': reference,
    })

def delete_pharmacy_order(request, pk):
    order = get_object_or_404(PharmacyOrder, pk=pk)
    log_action(request.user, order, 'suppression')  # Log suppression
    order.delete()
    request.session['swal_success'] = f"Commande {order.name} supprimée avec succès."
    return redirect('pharmacy_order_list')

def pharmacy_order_detail_json(request, order_id):
    order = get_object_or_404(PharmacyOrder, pk=order_id)
    supplier = get_object_or_404(PharmacySupplier, pk=order.supplier.id)
    order_lines = order.order_lines.all()

    order_data = {
        'name': order.name,
        'supplier': order.supplier.name,
        'date_order': order.date_order.strftime('%Y-%m-%d'),
        'state': order.get_state_display(),
        'state_code': order.state,
        'currency': order.currency.libelle,
        'notes': order.notes or 'Aucune',
        'amount_untaxed': str(order.amount_untaxed),
        'amount_tax': str(order.amount_tax),
        'amount_total': str(order.amount_total),
        'payment_mode': order.payment_mode.name if order.payment_mode else 'Non spécifié',
        'supplier_ref': order.supplier_ref or 'Non spécifiée',
    }

    lines_data = []
    for line in order_lines:
        tax_amount = Decimal('0.00')
        tax_display = 'Sans taxe'
        if line.tax and hasattr(line.tax, 'valeur'):
            tax_display = f"{line.tax.libelle} ({line.tax.valeur}%)"
            tax_amount = line.price_subtotal * (Decimal(str(line.tax.valeur)) / Decimal('100.0'))
        total_ttc = line.price_subtotal + tax_amount
        lines_data.append({
            'name': line.name,
            'product_qty': line.product_qty,
            'price_unit': str(line.price_unit),
            'taxes': [tax_display],
            'price_subtotal': str(line.price_subtotal),
            'tax_amount': str(tax_amount),
            'total_ttc': str(total_ttc),
        })

    supplier_data = {
        'id': supplier.id,
        'name': supplier.name,
        'address': supplier.street + (', ' + supplier.street2 if supplier.street2 else '') + (', ' + supplier.city.name if supplier.city else ''),
        'city': supplier.city.name if supplier.city else '',
    }

    return JsonResponse({'order': order_data, 'order_lines': lines_data, 'supplier': supplier_data})

@require_http_methods(["POST"])
@csrf_exempt
def confirm_pharmacy_order(request, order_id):
    order = get_object_or_404(PharmacyOrder, pk=order_id)
    if order.state == 'draft':
        data = request.POST or request.body
        if hasattr(data, 'decode'):  # si c'est du JSON brut
            data = json.loads(data.decode())
        supplier_ref = data.get('supplier_ref') if isinstance(data, dict) else request.POST.get('supplier_ref')
        payment_mode_id = data.get('payment_mode_id') if isinstance(data, dict) else request.POST.get('payment_mode_id')

        order.supplier_ref = supplier_ref or ''
        if payment_mode_id:
            order.payment_mode = get_object_or_404(PaymentMode, pk=payment_mode_id)

        if order.name.startswith('PHARM-PR-'):
            order.name = order.name.replace('PHARM-PR-', 'PHARM-PO-', 1)

        order.state = 'confirmed'
        order.save()
        log_action(request.user, order, 'confirmation')  # Log confirmation
        # Création du mouvement de stock réception
        User = get_user_model()
        if request.user.is_authenticated:
            created_by = request.user
        else:
            created_by = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not created_by:
            return JsonResponse({'success': False, 'error': "Aucun utilisateur authentifié pour créer le mouvement de stock."})

        try:

            reception_type = PharmacyOperationType.objects.filter(label__icontains='réception').first()
            if not reception_type:
                return JsonResponse({'success': False, 'error': "Type d'opération 'Réception' introuvable."})

            # Générer une référence unique
            next_id = (PharmacyStockMove.objects.aggregate(max_id=Max('move_id'))['max_id'] or 0) + 1
            reference = f"PHSTM-{next_id:05d}"

            stock_move = PharmacyStockMove.objects.create(
                supplier=order.supplier,
                reference=reference,
                state='draft',
                operation_type=reception_type,
                created_by=created_by,
                scheduled_date=order.date_order,
                order=order,
            )

            for line in order.order_lines.all():
                    PharmacyLineStockMove.objects.create(
                        move=stock_move,
                        product=line.product,
                        quantity_demanded=line.product_qty,
                        uom=line.product.uom,
                    )
                    log_action(request.user, line, 'creation')  # Log création de la ligne de mouvement
        except Exception as e:
            return JsonResponse({'success': False, 'error': f"Erreur création StockMove: {e}"})

        return JsonResponse({'success': True, 'redirect': '/pharmacy/orders/'})

    return JsonResponse({'success': False, 'error': 'Commande non en brouillon.'})

def get_pharmacy_orders(request):
    try:
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        supplier = request.GET.get('supplier', '')
        status = request.GET.get('status', '')
        
        orders = PharmacyOrder.objects.all().select_related('supplier')
        
        if start_date:
            orders = orders.filter(date_order__gte=start_date)
        if end_date:
            orders = orders.filter(date_order__lte=end_date)
        if supplier:
            orders = orders.filter(supplier_id=supplier)
        if status:
            orders = orders.filter(state=status)
        
        orders_data = [{
            'id': order.id,
            'name': order.name,
            'supplier_name': order.supplier.name if order.supplier else '',
            'date_order': order.date_order.strftime('%Y-%m-%d') if order.date_order else '',
            'amount_total': float(order.amount_total) if order.amount_total else 0,
            'state': order.state,
            'state_display': order.get_state_display(),
            'payment_mode': order.payment_mode.name if order.payment_mode else '',
        } for order in orders]
        
        return JsonResponse({'orders': orders_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@transaction.atomic
def edit_pharmacy_order(request, order_id):
    order = get_object_or_404(PharmacyOrder, id=order_id)
    
    PharmacyOrderLineFormSet = modelformset_factory(
        PharmacyOrderLine,
        form=PharmacyOrderLineForm,
        extra=0,
        can_delete=True
    )

    if request.method == 'POST':
        form = PharmacyOrderForm(request.POST, instance=order)
        formset = PharmacyOrderLineFormSet(
            request.POST,
            prefix='lines',
            queryset=order.order_lines.all()
        )

        if form.is_valid() and formset.is_valid():
            order = form.save()
            recalculate_pharmacy_totals(order)
            log_action(request.user, order, 'modification')  # Log modification
            request.session['swal_success'] = 'Commande modifiée avec succès.'
            return redirect('pharmacy_order_list')
        else:
            messages.error(request, 'Erreur dans le formulaire. Vérifiez les données saisies.')

    else:
        form = PharmacyOrderForm(instance=order)
        formset = PharmacyOrderLineFormSet(queryset=order.order_lines.all(), prefix='lines')

    context = {
        'form': form,
        'formset': formset,
        'order': order,
        'page_title': f'Modifier la commande {order.name}',
        'suppliers': PharmacySupplier.objects.all(),
        'currencies': Currency.objects.all(),
        'products': PharmacyProduct.objects.all(),
        'units': PharmacyUnitOfMesure.objects.all(),
        'taxes': Tax.objects.all(),
    }
    return render(request, 'edit_pharmacy_order.html', context)

def process_pharmacy_order_lines(formset, order):
    saved_lines = []
    for form in formset:
        if form.is_valid() and form.cleaned_data and not form.cleaned_data.get('DELETE'):
            product = form.cleaned_data.get('product')
            qty = form.cleaned_data.get('product_qty')
            price = form.cleaned_data.get('price_unit')
            if not product or qty is None or price is None:
                continue  # Skip incomplete lines
            line = form.save(commit=False)
            line.order = order
            line.price_subtotal = Decimal(str(qty)) * Decimal(str(price))
            if not line.name:
                line.name = str(product)
            line.save()
            saved_lines.append(line)
        elif form.cleaned_data.get('DELETE') and form.instance.pk:
            log_action(form.instance.user, form.instance, 'suppression')  # Log suppression
            form.instance.delete()
    return saved_lines

def recalculate_pharmacy_totals(order):
    total_untaxed = Decimal('0')
    total_tax = Decimal('0')
    lines = order.order_lines.all()
    for line in lines:
        total_untaxed += line.price_subtotal
        if line.tax and hasattr(line.tax, 'valeur'):
            tax_amount = line.price_subtotal * (Decimal(str(line.tax.valeur)) / Decimal('100'))
            total_tax += tax_amount
    order.amount_untaxed = total_untaxed
    order.amount_tax = total_tax
    order.amount_total = total_untaxed + total_tax
    order.save()

@require_http_methods(["POST"])
@csrf_exempt
def delete_pharmacy_order_line(request, line_id):
    try:
        line = get_object_or_404(PharmacyOrderLine, id=line_id)
        order = line.order
        log_action(request.user, line, 'suppression')  # Log suppression
        line.delete()
        recalculate_pharmacy_totals(order)
        return JsonResponse({"success": True, "message": "Ligne supprimée avec succès"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

@csrf_protect
@transaction.atomic
def duplicate_pharmacy_order(request, order_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée.'}, status=405)

    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        new_supplier_id = data.get('supplier_id')
        if not new_supplier_id:
            return JsonResponse({'success': False, 'error': 'ID du fournisseur manquant.'}, status=400)

        # Fetch original order and new supplier
        original_order = get_object_or_404(PharmacyOrder, pk=order_id)
        new_supplier = get_object_or_404(PharmacySupplier, pk=new_supplier_id)

        # Generate new reference
        try:
            if original_order.name.startswith('PHARM-PR-'):
                last_number = int(original_order.name.split('-')[-1])
                new_ref = f'PHARM-PR-{last_number + 1:06d}'
            else:
                # Fetch the latest order to generate a new reference
                last_order = PharmacyOrder.objects.filter(name__startswith='PHARM-PR-').order_by('-name').first()
                last_number = int(last_order.name.split('-')[-1]) if last_order else 0
                new_ref = f'PHARM-PR-{last_number + 1:06d}'
        except (ValueError, IndexError):
            return JsonResponse({'success': False, 'error': 'Format de référence invalide.'}, status=400)

        # Create duplicated order
        duplicated_order = PharmacyOrder.objects.create(
            name=new_ref,
            supplier=new_supplier,
            date_order=original_order.date_order,
            currency=original_order.currency,
            payment_mode=None,  # Set to None for draft orders
            amount_untaxed=Decimal('0.00'),
            amount_tax=Decimal('0.00'),
            amount_total=Decimal('0.00'),
            invoice_status='to_invoice',
            date_planned=original_order.date_planned,
            notes=original_order.notes,
            state='draft',
        )

        # Duplicate order lines
        total_untaxed = Decimal('0.00')
        total_tax = Decimal('0.00')
        for line in original_order.order_lines.all():
            tax_amount = Decimal('0.00')
            if line.tax and hasattr(line.tax, 'valeur') and line.tax.valeur is not None:
                tax_amount = line.price_subtotal * (Decimal(str(line.tax.valeur)) / Decimal('100.0'))

            PharmacyOrderLine.objects.create(
                order=duplicated_order,
                product=line.product,
                product_qty=line.product_qty,
                price_unit=line.price_unit,
                price_subtotal=line.price_subtotal,
                tax=line.tax,
                name=line.name,
            )
            total_untaxed += line.price_subtotal
            total_tax += tax_amount

        # Update totals
        duplicated_order.amount_untaxed = total_untaxed
        duplicated_order.amount_tax = total_tax
        duplicated_order.amount_total = total_untaxed + total_tax
        log_action(request.user, duplicated_order, 'duplication')  # Log duplication
        duplicated_order.save()

        return JsonResponse({'success': True, 'order_id': duplicated_order.id}, status=201)

    except PharmacySupplier.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Fournisseur non trouvé.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur serveur: {str(e)}'}, status=500)
def generate_pharmacy_order_pdf(request, order_id):
    json_data = pharmacy_order_detail_json(request, order_id).content
    context = json.loads(json_data)
    log_action(request.user, PharmacyOrder.objects.get(pk=order_id), 'impression')  # Log impression
    html_string = render_to_string('order_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="commande_pharmacie_{context["order"]["name"]}.pdf"'
    HTML(string=html_string).write_pdf(response)
    return response

def generate_pharmacy_price_request_pdf(request, order_id):
    json_data = pharmacy_order_detail_json(request, order_id).content
    context = json.loads(json_data)
    log_action(request.user, PharmacyOrder.objects.get(pk=order_id), 'impression')  # Log impression
    html_string = render_to_string('request_price_order.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="demande_prix_pharmacie_{context["order"]["name"]}.pdf"'
    HTML(string=html_string).write_pdf(response)
    return response

# ------------------------- PHARMACY STOCK MOVE --------------
# --- Helper to generate a unique reference ---
def _get_next_pharmacy_reference():
    last_id = PharmacyStockMove.objects.aggregate(max_id=Sum('move_id'))['max_id'] or 0
    return f'PHSM-{last_id + 1:04d}'

# --- List all pharmacy stock moves ---
def pharmacy_stock_move_list(request):
    moves = PharmacyStockMove.objects.select_related(
        'operation_type', 'source_location', 'dest_location',
        'department', 'supplier', 'created_by'
    ).prefetch_related('lines__product', 'lines__uom').order_by('-date_created')
    
    # Filtre par état
    state = request.GET.get('state', '')
    if state:
        moves = moves.filter(state=state)
    
    # Filtre par type d'opération
    operation_type = request.GET.get('operation_type', '')
    if operation_type:
        moves = moves.filter(operation_type__label=operation_type)
    
    # Recherche globale
    search = request.GET.get('search', '')
    if search:
        moves = moves.filter(
            Q(reference__icontains=search) |
            Q(operation_type__label__icontains=search) |
            Q(source_location__name__icontains=search) |
            Q(dest_location__name__icontains=search) |
            Q(department__name__icontains=search) |
            Q(supplier__name__icontains=search) |
            Q(notes__icontains=search)
        )
    
    paginator = Paginator(moves, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get all operation types for the filter
    operation_types = PharmacyOperationType.objects.all().order_by('label')

    # Récupérer les messages de session
    swal_success = request.session.pop('swal_success', None)
    swal_error = request.session.pop('swal_error', None)
    
    return render(request, 'pharmacy_stock_move_list.html', {
        'page_obj': page_obj,
        'page_title': 'Mouvements de Stock Pharmacie',
        'states': PharmacyStockMove.STATE_CHOICES,
        'current_state': state,
        'current_operation_type': operation_type,
        'operation_types': operation_types, 
        'search': search,
        'swal_success': swal_success,
        'swal_error': swal_error,
    })

# --- AJAX: Get confirmed pharmacy orders for a supplier ---
def get_pharmacy_supplier_orders(request):
    supplier_id = request.GET.get('supplier_id')
    orders = PharmacyOrder.objects.filter(supplier_id=supplier_id, state='confirmed')
    data = {
        "orders": [{"id": o.id, "name": o.name} for o in orders]
    }
    return JsonResponse(data)

# --- AJAX: Get order lines for a given pharmacy order ---
def get_pharmacy_order_lines(request):
    order_id = request.GET.get('order_id')
    if not order_id:
        return JsonResponse({"lines": []})
    try:
        lines = PharmacyOrderLine.objects.filter(order_id=order_id)
        data = {
            "lines": [{
                "product_id": l.product_id,
                "product_qty": float(l.product_qty or 0),
                "product_uom_id": l.product.uom_id if l.product and l.product.uom_id else None
            } for l in lines]
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"lines": [], "error": str(e)}, status=500)

# --- Helper to get available stock for a product/location ---
def get_pharmacy_available_qty(product_id, location_id):
    pl = PharmacyProductLocation.objects.filter(product_id=product_id, location_id=location_id).first()
    return float(pl.quantity_stored) if pl else 0

# --- Render the stock move form (create/edit) ---
def _render_pharmacy_stock_move_form(request, move_form, move_lines, move=None, edit=False):
    products_qs = PharmacyProduct.objects.select_related('uom').all()
    products_data = [
        {
            "id": p.pk,
            "short_label": p.short_label or p.full_label or p.brand or 'Produit sans nom',
            "full_label": p.full_label,
            "brand": p.brand,
            "uom_id": p.uom_id,
            "uom_label": p.uom.label if p.uom else "",
        }
        for p in products_qs
    ]
    # Stock par produit/emplacement (optionnel, pour d'autres besoins)
    product_locations = PharmacyProductLocation.objects.all()
    stock_by_product_location = {
        f"{pl.product.pk}_{pl.location.pk}": float(pl.quantity_stored or 0)
        for pl in product_locations
    }
    # Convertir en JSON pour le template
    stock_by_product_location_json = json.dumps(stock_by_product_location)
    # Pré-remplir les commandes du fournisseur si c'est une édition
    supplier_orders = []
    selected_order_id = ''
    if move and move.supplier:
        supplier_orders = PharmacyOrder.objects.filter(supplier=move.supplier, state='confirmed')
        # If model has order relationship, pre-select it; otherwise leave empty
        selected_order_id = getattr(move, 'order_id', '')
    return render(request, 'pharmacy_stock_move_form.html', {
        'move_form': move_form,
        'page_title': 'Éditer un Mouvement' if edit else 'Créer un Mouvement',
        'move': move,
        'products': products_data,
        'departments': Department.objects.all(),
        'suppliers': PharmacySupplier.objects.all(),
        'move_lines': move_lines,
        'stock_by_product_location': stock_by_product_location_json,
        'selected_order_id': selected_order_id,
        'supplier_orders': supplier_orders,
    })

# --- Create a pharmacy stock move ---
@transaction.atomic
def pharmacy_stock_move_create(request):
    if request.method == 'POST':
        move_form = PharmacyStockMoveForm(request.POST)
        try:
            lines = json.loads(request.POST.get('lines_json', '[]'))
        except Exception:
            lines = []
        validation_errors = []
        seen = set()
        for l in lines:
            if l.get('product') in seen:
                validation_errors.append("Un même produit ne peut pas être sélectionné plusieurs fois.")
            seen.add(l.get('product'))
        for l in lines:
            if not l.get('product') or float(l.get('quantity_demanded', 0)) <= 0:
                validation_errors.append("Chaque ligne doit avoir un produit et une quantité > 0.")
        operation_type = None
        operation_label = ''
        if move_form.is_valid():
            operation_type = move_form.cleaned_data.get('operation_type')
            operation_label = operation_type.label.lower() if operation_type else ''
        src = move_form.cleaned_data.get('source_location')
        dst = move_form.cleaned_data.get('dest_location')
        dept = move_form.cleaned_data.get('department')
        produits_deja_signales = set()
        for l in lines:
            product_id = l.get('product')
            qty_demanded = Decimal(str(l.get('quantity_demanded', 0)))
            qa_raw = l.get('quantity_arrived', 0)
            quantity_arrived = Decimal(str(qa_raw)) if str(qa_raw).strip() else Decimal('0')
            try:
                product = PharmacyProduct.objects.get(pk=product_id)
            except PharmacyProduct.DoesNotExist:
                validation_errors.append(f"Produit ID {product_id} n'existe pas.")
                continue
            if 'transfert' in operation_label or 'consommation' in operation_label:
                if src:
                    pl_src = PharmacyProductLocation.objects.filter(product_id=product_id, location=src).first()
                    if not pl_src:
                        if product_id not in produits_deja_signales:
                            validation_errors.append(f"Le produit {product.short_label} n'existe pas dans l'emplacement d'origine.")
                            produits_deja_signales.add(product_id)
                        continue
                    if qty_demanded > pl_src.quantity_stored:
                        if product_id not in produits_deja_signales:
                            validation_errors.append(
                                f"Produit {product.short_label}: Quantité demandée ({qty_demanded}) supérieure au stock disponible dans l'emplacement ({pl_src.quantity_stored})"
                            )
                            produits_deja_signales.add(product_id)
                        continue
                    if quantity_arrived > 0 and quantity_arrived > pl_src.quantity_stored:
                        if product_id not in produits_deja_signales:
                            validation_errors.append(
                                f"Produit {product.short_label}: Quantité arrivée ({quantity_arrived}) supérieure au stock disponible dans l'emplacement ({pl_src.quantity_stored})"
                            )
                            produits_deja_signales.add(product_id)
                        continue
        if validation_errors:
            for error in validation_errors:
                move_form.add_error(None, error)
            return _render_pharmacy_stock_move_form(request, move_form, lines)
        if move_form.is_valid():
            move = move_form.save(commit=False)
            if not move.reference:
                move.reference = _get_next_pharmacy_reference()

            order_id = request.POST.get('order')
            if order_id and order_id != '-------' and hasattr(move, 'order_id'):
                move.order_id = int(order_id) if order_id.isdigit() else None

            action = request.POST.get('action', 'save')
            move.state = {
                'save': 'draft',
                'confirm': 'confirmed',
                'done': 'done',
                'cancel': 'canceled'
            }.get(action, 'draft')
            move.save()
            log_action(request.user, move, 'creation')  # Log création
            PharmacyLineStockMove.objects.filter(move=move).delete()
            for l in lines:
                if l.get('product') and l.get('quantity_demanded') and l.get('uom'):
                    PharmacyLineStockMove.objects.create(
                        move=move,
                        product_id=int(l['product']),
                        quantity_demanded=safe_decimal(l['quantity_demanded']),
                        uom_id=l['uom'],
                        quantity_arrived=safe_decimal(l.get('quantity_arrived', 0))
                    )
            if move.state == 'done':
                for l in lines:
                    product_id = int(l['product'])
                    qty_demanded = Decimal(str(l.get('quantity_demanded', 0)))
                    qty_arrived = safe_decimal(l.get('quantity_arrived', 0))
                    src = move.source_location
                    dst = move.dest_location
                    dept = move.department
                    if 'transfert' in operation_label:
                        if src:
                            pl_src, _ = PharmacyProductLocation.objects.get_or_create(
                                product_id=product_id, location=src, defaults={'quantity_stored': 0}
                            )
                            pl_src.quantity_stored -= qty_arrived
                            pl_src.save()
                        if dst:
                            pl_dst, _ = PharmacyProductLocation.objects.get_or_create(
                                product_id=product_id, location=dst, defaults={'quantity_stored': 0}
                            )
                            pl_dst.quantity_stored += qty_arrived
                            pl_dst.save()
                    elif 'réception' in operation_label:
                        if dst:
                            pl_dst, _ = PharmacyProductLocation.objects.get_or_create(
                                product_id=product_id, location=dst, defaults={'quantity_stored': 0}
                            )
                            pl_dst.quantity_stored += qty_arrived
                            pl_dst.save()
                    elif 'consommation' in operation_label:
                        if src:
                            pl_src, _ = PharmacyProductLocation.objects.get_or_create(
                                product_id=product_id, location=src, defaults={'quantity_stored': 0}
                            )
                            pl_src.quantity_stored -= qty_arrived
                            pl_src.save()
                        if dept:
                            ipd, _ = PharmacyProductDepartment.objects.get_or_create(
                                product_id=product_id, department=dept, defaults={'quantity_stored': 0}
                            )
                            ipd.quantity_stored += qty_arrived
                            ipd.save()
                    product = PharmacyProduct.objects.get(pk=product_id)
                    total = PharmacyProductLocation.objects.filter(product=product).aggregate(total=Sum('quantity_stored'))['total'] or 0
                    product.total_quantity_cached = total
                    product.save(update_fields=['total_quantity_cached'])
                move.effective_date = timezone.now().date()
                move.save()
                request.session['swal_success'] = "Mouvement validé avec succès. Les stocks ont été mis à jour."
                return redirect('pharmacy_stock_move_list')

            else:  # 'draft' or 'confirm' or 'cancel'
                if action == 'draft':
                    request.session['swal_success'] = "Mouvement sauvegardé comme brouillon."
                elif action == 'confirm':
                    request.session['swal_success'] = "Mouvement confirmé avec succès."
                elif action == 'cancel':
                    request.session['swal_success'] = "Mouvement annulé."
                else:
                    request.session['swal_success'] = "Mouvement sauvegardé avec succès."
                return redirect('pharmacy_stock_move_list')
        else:
            return _render_pharmacy_stock_move_form(request, move_form, lines)
    else:
        move_form = PharmacyStockMoveForm()
        return _render_pharmacy_stock_move_form(request, move_form, [])

# --- Update a pharmacy stock move ---
@transaction.atomic
def pharmacy_stock_move_update(request, pk):
    move = get_object_or_404(PharmacyStockMove, pk=pk)
    if request.method == 'POST':
        move_form = PharmacyStockMoveForm(request.POST, instance=move)
        try:
            lines = json.loads(request.POST.get('lines_json', '[]'))
        except Exception:
            lines = []
        validation_errors = []
        seen = set()
        for l in lines:
            if l.get('product') in seen:
                validation_errors.append("Un même produit ne peut pas être sélectionné plusieurs fois.")
            seen.add(l.get('product'))
        for l in lines:
            if not l.get('product') or float(l.get('quantity_demanded', 0)) <= 0:
                validation_errors.append("Chaque ligne doit avoir un produit et une quantité > 0.")
        operation_type = None
        operation_label = ''
        if move_form.is_valid():
            operation_type = move_form.cleaned_data.get('operation_type')
            operation_label = operation_type.label.lower() if operation_type else ''
        src = move_form.cleaned_data.get('source_location')
        dst = move_form.cleaned_data.get('dest_location')
        dept = move_form.cleaned_data.get('department')
        produits_deja_signales = set()
        for l in lines:
            product_id = l.get('product')
            qty_demanded = Decimal(str(l.get('quantity_demanded', 0)))
            qa_raw = l.get('quantity_arrived', 0)
            quantity_arrived = Decimal(str(qa_raw)) if str(qa_raw).strip() else Decimal('0')
            try:
                product = PharmacyProduct.objects.get(pk=product_id)
            except PharmacyProduct.DoesNotExist:
                validation_errors.append(f"Produit ID {product_id} n'existe pas.")
                continue
            if 'transfert' in operation_label or 'consommation' in operation_label:
                if src:
                    pl_src = PharmacyProductLocation.objects.filter(product_id=product_id, location=src).first()
                    if not pl_src:
                        if product_id not in produits_deja_signales:
                            validation_errors.append(f"Le produit {product.short_label} n'existe pas dans l'emplacement d'origine.")
                            produits_deja_signales.add(product_id)
                        continue
                    if qty_demanded > pl_src.quantity_stored:
                        if product_id not in produits_deja_signales:
                            validation_errors.append(
                                f"Produit {product.short_label}: Quantité demandée ({qty_demanded}) supérieure au stock disponible dans l'emplacement ({pl_src.quantity_stored})"
                            )
                            produits_deja_signales.add(product_id)
                        continue
                    if quantity_arrived > 0 and quantity_arrived > pl_src.quantity_stored:
                        if product_id not in produits_deja_signales:
                            validation_errors.append(
                                f"Produit {product.short_label}: Quantité arrivée ({quantity_arrived}) supérieure au stock disponible dans l'emplacement ({pl_src.quantity_stored})"
                            )
                            produits_deja_signales.add(product_id)
                        continue
        if validation_errors:
            for error in validation_errors:
                move_form.add_error(None, error)
            return _render_pharmacy_stock_move_form(request, move_form, lines, move=move, edit=True)
        if move_form.is_valid():
            move = move_form.save(commit=False)
            if not move.reference:
                move.reference = _get_next_pharmacy_reference()

            order_id = request.POST.get('order')
            if order_id and order_id != '-------' and hasattr(move, 'order_id'):
                move.order_id = int(order_id) if order_id.isdigit() else None

            action = request.POST.get('action', 'save')
            move.state = {
                'save': 'draft',
                'confirm': 'confirmed',
                'done': 'done',
                'cancel': 'canceled'
            }.get(action, 'draft')
            move.save()
            log_action(request.user, move, 'modification')  # Log modification
            PharmacyLineStockMove.objects.filter(move=move).delete()
            for l in lines:
                if l.get('product') and l.get('quantity_demanded') and l.get('uom'):
                    PharmacyLineStockMove.objects.create(
                        move=move,
                        product_id=int(l['product']),
                        quantity_demanded=safe_decimal(l['quantity_demanded']),
                        uom_id=l['uom'],
                        quantity_arrived=safe_decimal(l.get('quantity_arrived', 0))
                    )
            if move.state == 'done':
                for l in lines:
                    product_id = int(l['product'])
                    qty_demanded = Decimal(str(l.get('quantity_demanded', 0)))
                    qty_arrived = Decimal(str(l.get('quantity_arrived', 0))) if l.get('quantity_arrived') else qty_demanded
                    if 'transfert' in operation_label:
                        if src:
                            pl_src = PharmacyProductLocation.objects.filter(product_id=product_id, location=src).first()
                            if pl_src:
                                pl_src.quantity_stored = max(Decimal('0'), pl_src.quantity_stored - qty_demanded)
                                pl_src.save()
                        if dst:
                            pl_dest, _ = PharmacyProductLocation.objects.get_or_create(
                                product_id=product_id, location=dst, defaults={'quantity_stored': 0}
                            )
                            pl_dest.quantity_stored += qty_arrived
                            pl_dest.save()
                    elif 'réception' in operation_label:
                        if dst:
                            pl_dest, _ = PharmacyProductLocation.objects.get_or_create(
                                product_id=product_id, location=dst, defaults={'quantity_stored': 0}
                            )
                            pl_dest.quantity_stored += qty_arrived
                            pl_dest.save()
                    elif 'consommation' in operation_label:
                        if src:
                            pl_src = PharmacyProductLocation.objects.filter(product_id=product_id, location=src).first()
                            if pl_src:
                                pl_src.quantity_stored = max(Decimal('0'), pl_src.quantity_stored - qty_demanded)
                                pl_src.save()
                        if dept:
                            ipd, _ = PharmacyProductDepartment.objects.get_or_create(
                                product_id=product_id, department=dept, defaults={'quantity_stored': 0}
                            )
                            ipd.quantity_stored += qty_arrived
                            ipd.save()
                    product = PharmacyProduct.objects.get(pk=product_id)
                    total = PharmacyProductLocation.objects.filter(product=product).aggregate(total=Sum('quantity_stored'))['total'] or 0
                    product.total_quantity_cached = total
                    product.save(update_fields=['total_quantity_cached'])
                move.effective_date = timezone.now().date()
                move.save()
                request.session['swal_success'] = "Mouvement validé avec succès. Les stocks ont été mis à jour."
                return redirect('pharmacy_stock_move_list')
            else:
                action = request.POST.get('action', 'save')
                if action == 'draft':
                    request.session['swal_success'] = "Mouvement sauvegardé comme brouillon."
                elif action == 'confirm':
                    request.session['swal_success'] = "Mouvement confirmé avec succès."
                elif action == 'cancel':
                    request.session['swal_success'] = "Mouvement annulé."
                else:
                    request.session['swal_success'] = "Mouvement sauvegardé avec succès."
                return redirect('pharmacy_stock_move_list')
        else:
            return _render_pharmacy_stock_move_form(request, move_form, lines, move=move, edit=True)
    else:
        move_form = PharmacyStockMoveForm(instance=move)
        move_lines = list(move.lines.values('product_id', 'quantity_demanded', 'uom_id', 'quantity_arrived'))
        move_lines = [
            {
                'product_id': l['product_id'],
                'quantity_demanded': float(l['quantity_demanded']),
                'uom_id': l['uom_id'],
                'quantity_arrived': float(l['quantity_arrived']) if l['quantity_arrived'] is not None else 0
            } for l in move_lines
        ]
        return _render_pharmacy_stock_move_form(request, move_form, move_lines, move=move, edit=True)

# --- Delete a pharmacy stock move ---
@transaction.atomic
def pharmacy_stock_move_delete(request, pk):
    move = get_object_or_404(PharmacyStockMove, pk=pk)
    if request.method == 'POST':
        try:
            log_action(request.user, move, 'suppression')  # Log suppression
            move_ref = move.reference
            move.delete()
            request.session['swal_success'] = f"Mouvement {move_ref} supprimé avec succès."
            return redirect('pharmacy_stock_move_list')
        except Exception as e:
            request.session['swal_error'] = f"Erreur lors de la suppression du mouvement : {e}"
            return redirect('pharmacy_stock_move_list')
    return render(request, 'pharmacy_confirm_delete.html', {
        'object': move,
        'page_title': 'Confirmer la suppression',
        'cancel_url': 'pharmacy_stock_move_list',
    })

# --- Stock move detail as JSON for API/export ---
def pharmacy_stock_move_detail_json(request, pk):
    move = get_object_or_404(
        PharmacyStockMove.objects.select_related(
            'source_location', 'dest_location', 'operation_type', 'created_by'
        ).prefetch_related('lines__product', 'lines__uom'),
        pk=pk
    )
    data = {
        'id': move.pk,
        'reference': move.reference,
        'supplier': move.supplier.name if move.supplier else None,
        'state': move.state,
        'scheduled_date': move.scheduled_date,
        'effective_date': move.effective_date,
        'source_location': move.source_location.name if move.source_location else None,
        'dest_location': move.dest_location.name if move.dest_location else None,
        'operation_type': move.operation_type.label if move.operation_type else None,
        'created_by': move.created_by.username,
        'lines': [
            {
                'product': line.product.short_label,
                'quantity_demanded': line.quantity_demanded,
                'quantity_arrived': line.quantity_arrived,
                'uom': line.uom.label,
            } for line in move.lines.all()
        ],
    }
    return JsonResponse(data, json_dumps_params={'indent': 2})

# --- Global PDF for all stock moves ---
def pharmacy_stock_move_pdf(request):
    state = request.GET.get('state', '')
    moves = PharmacyStockMove.objects.select_related('operation_type', 'source_location', 'dest_location', 'department', 'supplier').prefetch_related('lines__product', 'lines__uom').all()
    if state:
        moves = moves.filter(state=state)
    log_action(request.user, moves.first(), 'impression')  # Log impression (using first move as instance)
    template = render_to_string('pharmacy_stock_move_report.html', {'moves': moves, 'date': timezone.now().strftime('%Y-%m-%d %H:%M:%S')})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="pharmacy_stock_movements_report.pdf"'
    HTML(string=template, base_url=request.build_absolute_uri('/')).write_pdf(
        response,
        stylesheets=[CSS(string='''
            @page { margin: 1in; size: A4; }
            body { font-family: sans-serif; font-size: 12pt; }
            h1 { text-align: center; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .lines-table { margin-left: 20px; width: 80%; }
            .state-draft { color: blue; }
            .state-confirmed { color: orange; }
            .state-done { color: green; }
            .state-canceled { color: gray; }
        ''')]
    )
    return response

# --- PDF for a single validated stock move ---
@require_GET
def pharmacy_stock_move_delivery_pdf(request, pk):
    move = get_object_or_404(
        PharmacyStockMove.objects.select_related(
            'source_location', 'dest_location', 'operation_type', 'department', 'supplier', 'created_by'
        ).prefetch_related('lines__product', 'lines__uom'),
        pk=pk, state=PharmacyStockMove.DONE
    )
    log_action(request.user, move, 'impression')  # Log impression
    context = {
        'move': move,
        'lines': move.lines.all(),
        'date': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
        'page_title': 'Bon de Livraison Pharmacie',
    }
    html_string = render_to_string('pharmacy_stock_move_delivery_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pharmacy_delivery_{move.reference}.pdf"'
    HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(response)
    return response



def pharmacy_inventory_adjustment(request):
    if request.method == 'POST':
        updated_count = 0
        with transaction.atomic():
            product_locations = PharmacyProductLocation.objects.select_related('product', 'location').all()

            for pl in product_locations:
                input_key = f'counted_{pl.id}'
                counted_qty = request.POST.get(input_key, '').strip()

                try:
                    if counted_qty != '' and counted_qty is not None:
                        qty = float(counted_qty)
                        if qty < 0:
                            request.session['swal_error'] = f'Quantité négative non autorisée pour {pl.product.short_label} @ {pl.location.name}.'
                            return redirect('pharmacy_inventory_adjustment')
                        
                        pl.quantity_counted = qty
                        pl.last_count_date = timezone.now().date()
                        pl.save()
                        log_action(request.user, pl, 'modification')  # Log modification
                        updated_count += 1
                except ValueError:
                    request.session['swal_error'] = f'Valeur invalide pour {pl.product.short_label} @ {pl.location.name}.'
                    return redirect('pharmacy_inventory_adjustment')

        request.session['swal_success'] = 'Emplacements ajustés avec succès.'
        return redirect('pharmacy_inventory_adjustment')

    swal_success = request.session.pop('swal_success', None)
    swal_error = request.session.pop('swal_error', None)

    locations_list = PharmacyProductLocation.objects.select_related('product', 'location').order_by('product__code')
    paginator = Paginator(locations_list, 5)
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'pharmacy_inventory_adjustment.html', {
        'page_title': 'Ajustement de l\'Inventaire Pharmaceutique',
        'page_obj': page_obj,
        'swal_success': swal_success,
        'swal_error': swal_error,
    })


def pharmacy_inventory_adjustment_pdf(request):
    locations = PharmacyProductLocation.objects.select_related('product', 'location').order_by('product__code')
    adjusted_locations = []
    total_diff_cost = Decimal('0.0')

    for loc in locations:
        quantity_counted = loc.quantity_counted if loc.quantity_counted is not None else Decimal('0.0')
        quantity_stored = loc.quantity_stored if loc.quantity_stored is not None else Decimal('0.0')
        if quantity_counted != quantity_stored:
            unit_price = Decimal(str(loc.product.unit_price or 0.0))
            loc.diff = quantity_counted - quantity_stored
            loc.diff_value = loc.diff * unit_price
            total_diff_cost += loc.diff_value
            adjusted_locations.append(loc)

    log_action(request.user, locations.first(), 'impression')  # Log impression (using first location as instance)
    html_string = render_to_string('pharmacy_inventory_adjustment_pdf.html', {
        'page_title': "Rapport d'Ajustement d'Inventaire Pharmaceutique",
        'date': timezone.now().date(),
        'locations': adjusted_locations,
        'total_diff_cost': total_diff_cost,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pharmacy_adjustment_{timezone.now().date().strftime("%Y%m%d")}.pdf"'
    HTML(string=html_string).write_pdf(response)
    return response

# ------------------------EXPORT pharmacy product pdf------------------------------------------------------------------

def pharmacy_product_export(request):
     
    """
    Export pharmacy products to PDF with support for:
    - Selected IDs (`ids`)
    - Export all filtered items across all pages (`select_all=true`)
    - Server-side sorting (`sort_by`, `sort_order`)
    The logic mirrors inventory module behaviour.
    """
    query = request.GET.get('q', '')
    pharmaceutical_form_filter = request.GET.get('pharmaceutical_form', '')
    selected_ids = request.GET.get('ids', '')
    select_all = request.GET.get('select_all', '')
    sort_by = request.GET.get('sort_by', 'product_id')
    sort_order = request.GET.get('sort_order', 'desc')

    # Mapping of sortable fields to ORM fields
    sort_mapping = {
        'code': 'code',
        'short_label': 'short_label',
        'brand': 'brand',
        'dci': 'dci__label',
        'pharmaceutical_form': 'pharmaceutical_form__name',
        'unit_price': 'unit_price',
        'total_quantity_cached': 'total_quantity_cached',
        'product_id': 'product_id',
    }
    sort_field = sort_mapping.get(sort_by, 'product_id')
    order_prefix = '-' if sort_order == 'desc' else ''

    # Base queryset with sorting applied
    products = PharmacyProduct.objects.all().order_by(f'{order_prefix}{sort_field}')

    # If select_all is true, export all filtered products (across pages)
    if select_all == 'true':
        if query:
            products = products.filter(
                Q(code__icontains=query) |
                Q(short_label__icontains=query) |
                Q(brand__icontains=query) |
                Q(full_label__icontains=query) |
                Q(dci__label__icontains=query) |
                Q(pharmaceutical_form__name__icontains=query) |
                Q(dosage__icontains=query) |
                Q(unit_price__icontains=query) |
                Q(total_quantity_cached__icontains=query) |
                Q(barcode__icontains=query)
            )
        if pharmaceutical_form_filter:
            products = products.filter(pharmaceutical_form__name=pharmaceutical_form_filter)
        return _generate_pharmacy_export_pdf(request, products, query, pharmaceutical_form_filter)

    # If specific product IDs are provided
    if selected_ids:
        try:
            ids_list = [int(pk.strip()) for pk in selected_ids.split(',') if pk.strip().isdigit()]
            if ids_list:
                products = products.filter(product_id__in=ids_list)
                return _generate_pharmacy_export_pdf(request, products, query, pharmaceutical_form_filter)
        except (ValueError, AttributeError):
            # Malformed IDs – fall back to normal flow
            pass

    # Fallback: apply filters if neither select_all nor ids mode
    if query:
        products = products.filter(
            Q(code__icontains=query) |
            Q(short_label__icontains=query) |
            Q(brand__icontains=query) |
            Q(full_label__icontains=query) |
            Q(dci__label__icontains=query) |
            Q(pharmaceutical_form__name__icontains=query) |
            Q(dosage__icontains=query) |
            Q(unit_price__icontains=query) |
            Q(total_quantity_cached__icontains=query) |
            Q(barcode__icontains=query)
        )
    if pharmaceutical_form_filter:
        products = products.filter(pharmaceutical_form__name=pharmaceutical_form_filter)

    if products.exists():
        log_action(request.user, products.first(), 'impression')

    return _generate_pharmacy_export_pdf(request, products, query, pharmaceutical_form_filter)
    query = request.GET.get('q', '')
    pharmaceutical_form_filter = request.GET.get('pharmaceutical_form', '')
    
    products = PharmacyProduct.objects.all().order_by('-product_id')
    
    if query:
        products = products.filter(
            Q(code__icontains=query) |
            Q(short_label__icontains=query) |
            Q(brand__icontains=query) |
            Q(full_label__icontains=query) |
            Q(dci__label__icontains=query) |
            Q(pharmaceutical_form__name__icontains=query) |
            Q(dosage__icontains=query) |
            Q(unit_price__icontains=query) |
            Q(total_quantity_cached__icontains=query) |
            Q(barcode__icontains=query)
        )
    
    if pharmaceutical_form_filter:
        products = products.filter(pharmaceutical_form__name=pharmaceutical_form_filter)
    
    log_action(request.user, products.first(), 'impression')  # Log impression (using first product as instance)
    
    return _generate_pharmacy_export_pdf(request, products, query, pharmaceutical_form_filter)


def _generate_pharmacy_export_pdf(request, products, query='', pharmaceutical_form_filter=''):
    html_string = render_to_string('pharmacy_product_export_pdf.html', {
        'products': products,
        'query': query,
        'pharmaceutical_form_filter': pharmaceutical_form_filter,
        'export_date': timezone.now(),
    })
    
    pdf = HTML(string=html_string).write_pdf()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="produits_pharmaceutiques_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    return response


# ===================================================================
# INVENTORY VIEWS - Similar to inventory module
# ===================================================================

def pharmacy_inventory_list(request):
    """Vue pour afficher la liste d'inventaire des produits pharmacy - similaire à inventory_list"""
    # Get all categories for the filter
    categories = PharmacyProductCategory.objects.all().order_by('label')
    
    return render(request, 'pharmacy_inventory.html', {
        'page_title': 'Inventaire des Produits Pharmaceutiques',
        'categories': categories,
        'current_category': request.GET.get('category', ''),
    })

def pharmacy_inventory_list_json(request):
    """Vue JSON pour l'inventaire pharmacy - similaire à inventory_list_json"""
    page_number = request.GET.get('page', 1)
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    sort_by = request.GET.get('sort_by', 'code')
    sort_order = request.GET.get('sort_order', 'asc')

    products = PharmacyProduct.objects.all()
    
    # Filter by category if provided
    if category:
        products = products.filter(categ__label=category)
    
    # Search by multiple fields
    if query:
        normalized_query = query.replace(',', '.')
        
        products = products.filter(
            Q(short_label__icontains=query) |
            Q(code__icontains=query) |
            Q(categ__label__icontains=query) |
            Q(total_quantity_cached__icontains=normalized_query) |
            Q(brand__icontains=query) |
            Q(full_label__icontains=query) |
            Q(dci__label__icontains=query) |
            Q(pharmaceutical_form__name__icontains=query)
        )

    # Apply sorting
    sort_field_mapping = {
        'default_code': 'code',
        'name': 'short_label',
        'category': 'categ__label',
        'total_quantity': 'total_quantity'
    }
    
    django_field = sort_field_mapping.get(sort_by, 'code')
    if sort_order == 'desc':
        django_field = f'-{django_field}'
    
    products = products.order_by(django_field)

    paginator = Paginator(products, 5)
    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(1)

    product_data = []
    for product in page_obj:
        product_locations = list(
            PharmacyProductLocation.objects.filter(product=product)
            .values('location', 'quantity_stored', 'location__name')
        )
        for loc in product_locations:
            loc['location_id'] = loc.pop('location')  
            loc['quantity_stored'] = float(loc['quantity_stored'])
            loc['location_name'] = loc.pop('location__name')
        product_data.append({
            'id': product.pk,
            'name': product.short_label,
            'default_code': product.code,
            'category': product.categ.label if product.categ else '',
            'standard_price': float(product.unit_price) if product.unit_price else 0.0,
            'total_quantity': float(product.total_quantity) if product.total_quantity else 0.0,
            'locations': product_locations,
        })

    pagination = {
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'page_range': list(paginator.page_range),
    }

    return JsonResponse({
        'products': product_data,
        'pagination': pagination,
    })

def pharmacy_inventory_pdf(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    products = PharmacyProduct.objects.all().order_by('-product_id')
    
    if category:
        products = products.filter(categ__label=category)
    
    if query:
        normalized_query = query.replace(',', '.')
        products = products.filter(
            Q(short_label__icontains=query) |
            Q(code__icontains=query) |
            Q(categ__label__icontains=query) |
            Q(total_quantity_cached__icontains=normalized_query) |
            Q(brand__icontains=query) |
            Q(full_label__icontains=query) |
            Q(dci__label__icontains=query) |
            Q(pharmaceutical_form__name__icontains=query)
        )
    
    product_data = []
    for product in products:
        product_locations = list(
            PharmacyProductLocation.objects.filter(product=product)
            .values('location', 'quantity_stored', 'location__name')
        )
        for loc in product_locations:
            loc['location_id'] = loc.pop('location')
            loc['quantity_stored'] = float(loc['quantity_stored'])
            loc['location_name'] = loc.pop('location__name')
        product_data.append({
            'id': product.pk,
            'name': product.short_label,
            'default_code': product.code,
            'category': product.categ.label if product.categ else '',
            'standard_price': float(product.unit_price) if product.unit_price else 0.0,
            'total_quantity': float(product.total_quantity) if product.total_quantity else 0.0,
            'locations': product_locations,
        })

    log_action(request.user, products.first(), 'impression')  # Log impression (using first product as instance)
    html_string = render_to_string('pharmacy_inventory_pdf.html', {
        'products': product_data,
        'date': timezone.now().date().strftime('%Y-%m-%d'),
        'page_title': 'Inventaire des Produits Pharmaceutiques',
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pharmacy_inventory_{timezone.now().date().strftime("%Y%m%d")}.pdf"'
    HTML(string=html_string).write_pdf(response)
    return response




@require_http_methods(["GET"])
def pharmacy_product_order_history(request, pk):
    """
    Returns JSON data for a pharmacy product's order history, including unit prices, turnover, and price progression.
    
    Args:
        request: HTTP request object.
        pk: Primary key of the pharmacy product.
    
    Returns:
        JsonResponse with total order count, turnover, price progression data, and order details.
    """
    try:
        product = get_object_or_404(PharmacyProduct, pk=pk)
        order_lines = PharmacyOrderLine.objects.filter(
            product=product,
            order__state='confirmed'
        ).select_related('order__currency', 'order')
        
        # Total order count and turnover
        total_orders = order_lines.count()
        turnover = sum(float(line.price_subtotal) for line in order_lines if line.price_subtotal)
        
        # Price progression data (group by month)
        price_progression = (
            order_lines
            .annotate(month=TruncMonth('order__date_order'))
            .values('month')
            .annotate(
                avg_price=Avg('price_unit'),
                total_turnover=Sum('price_subtotal')
            )
            .order_by('month')
        )
        price_labels = [entry['month'].strftime('%Y-%m') if entry['month'] else 'N/A' for entry in price_progression]
        price_data = [float(entry['avg_price']) if entry['avg_price'] else 0 for entry in price_progression]
        turnover_data = [float(entry['total_turnover']) if entry['total_turnover'] else 0 for entry in price_progression]
        
        # Order details
        order_details = [{
            'order_id': line.order.id,
            'order_name': line.order.name,
            'date_order': line.order.date_order.strftime('%Y-%m-%d') if line.order.date_order else 'N/A',
            'unit_price': float(line.price_unit) if line.price_unit else 0,
            'quantity': float(line.product_qty) if line.product_qty else 0,
            'subtotal': float(line.price_subtotal) if line.price_subtotal else 0,
            'currency': line.order.currency.abreviation if line.order.currency else 'N/A',
            'state': line.order.get_state_display()
        } for line in order_lines]
        
        return JsonResponse({
            'success': True,
            'product_name': product.short_label,
            'total_orders': total_orders,
            'turnover': turnover,
            'chart_data': {
                'labels': price_labels,
                'prices': price_data,
                'turnover': turnover_data
            },
            'orders': order_details
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_http_methods(["GET"])
def pharmacy_product_order_history_pdf(request, pk):
    try:
        product = get_object_or_404(PharmacyProduct, pk=pk)
        order_lines = PharmacyOrderLine.objects.filter(
            product=product,
            order__state='confirmed'
        ).select_related('order__currency', 'order')
        
        total_orders = order_lines.count()
        turnover = sum(float(line.price_subtotal) for line in order_lines if line.price_subtotal)
        
        price_progression = (
            order_lines
            .annotate(month=TruncMonth('order__date_order'))
            .values('month')
            .annotate(
                avg_price=Avg('price_unit'),
                total_turnover=Sum('price_subtotal')
            )
            .order_by('month')
        )
        price_data = [
            {
                'month': entry['month'].strftime('%Y-%m') if entry['month'] else 'N/A',
                'avg_price': float(entry['avg_price']) if entry['avg_price'] else 0,
                'total_turnover': float(entry['total_turnover']) if entry['total_turnover'] else 0
            }
            for entry in price_progression
        ]
        
        order_details = [
            {
                'order_name': line.order.name,
                'date_order': line.order.date_order.strftime('%Y-%m-%d') if line.order.date_order else 'N/A',
                'unit_price': float(line.price_unit) if line.price_unit else 0,
                'quantity': float(line.product_qty) if line.product_qty else 0,
                'subtotal': float(line.price_subtotal) if line.price_subtotal else 0,
                'currency': line.order.currency.abreviation if line.order.currency else 'N/A',
                'state': line.order.get_state_display()
            }
            for line in order_lines
        ]
        
        context = {
            'product': {
                'name': product.short_label,
                'default_code': product.code or 'N/A',
                'category': product.categ.label if product.categ else 'N/A',
                'uom': product.uom.label if product.uom else 'N/A'
            },
            'total_orders': total_orders,
            'turnover': turnover,
            'price_data': price_data,
            'orders': order_details,
            'current_date': timezone.now().strftime('%Y-%m-%d'),
        }
        
        log_action(request.user, product, 'impression')  # Log impression
        html_string = render_to_string('pharmacy_product_order_history_pdf.html', context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="pharmacy_order_history_{product.short_label.replace(" ", "_")}.pdf"'
        HTML(string=html_string).write_pdf(response)
        return response
    except Exception as e:
        return HttpResponse(f"Erreur lors de la génération du PDF : {str(e)}", status=500)

@require_http_methods(["GET"])
def pharmacy_supplier_order_history(request, pk):
    """
    Returns JSON data for a pharmacy supplier's order history, including total count, turnover, orders by state, and order details.
    
    Args:
        request: HTTP request object.
        pk: Primary key of the pharmacy supplier.
    
    Returns:
        JsonResponse with total order count, turnover, orders by state for chart, and order details for table.
    """
    try:
        supplier = get_object_or_404(PharmacySupplier, pk=pk)
        orders = PharmacyOrder.objects.filter(
            supplier=supplier,
            state='confirmed'
        ).select_related('currency')
        
        # Total order count and turnover
        total_orders = orders.count()
        turnover = orders.aggregate(total=Sum('amount_total'))['total'] or 0.0
        turnover = float(turnover)
        
        # Orders by state for chart
        orders_by_state = orders.values('state').annotate(count=Count('id')).order_by('state')
        state_labels = []
        state_data = []
        for entry in orders_by_state:
            state_label = dict(PharmacyOrder.STATE_CHOICES).get(entry['state'], entry['state'])
            state_labels.append(state_label)
            state_data.append(entry['count'])
        
        # Order details for table
        order_details = [{
            'id': order.id,
            'name': order.name,
            'date_order': order.date_order.strftime('%Y-%m-%d') if order.date_order else 'N/A',
            'amount_total': float(order.amount_total) if order.amount_total else 0,
            'state': order.get_state_display(),
            'currency': 'MAD'  # Force currency to MAD
        } for order in orders]
        
        return JsonResponse({
            'success': True,
            'supplier_name': supplier.name,
            'total_orders': total_orders,
            'turnover': turnover,
            'chart_data': {
                'labels': state_labels,
                'data': state_data
            },
            'orders': order_details
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
@require_http_methods(["GET"])
def pharmacy_supplier_order_history_pdf(request, pk):
    try:
        supplier = get_object_or_404(PharmacySupplier, pk=pk)
        orders = PharmacyOrder.objects.filter(
            supplier=supplier,
            state='confirmed'
        ).select_related('currency')
        
        total_orders = orders.count()
        turnover = orders.aggregate(total=Sum('amount_total'))['total'] or 0.0
        turnover = float(turnover)
        
        orders_by_state = orders.values('state').annotate(count=Count('id')).order_by('state')
        state_data = [
            {
                'state': dict(PharmacyOrder.STATE_CHOICES).get(entry['state'], entry['state']),
                'count': entry['count']
            }
            for entry in orders_by_state
        ]
        
        order_details = [
            {
                'name': order.name,
                'date_order': order.date_order.strftime('%Y-%m-%d') if order.date_order else 'N/A',
                'amount_total': float(order.amount_total) if order.amount_total else 0,
                'state': order.get_state_display(),
                'currency': 'MAD'
            }
            for order in orders
        ]
        
        context = {
            'supplier': {
                'name': supplier.name,
                'email': supplier.email or 'N/A',
                'phone': supplier.phone or 'N/A',
                'address': f"{supplier.street} {supplier.street2 or ''}, {supplier.city.name if supplier.city else ''}, {supplier.country.name if supplier.country else ''}".strip(),
            },
            'total_orders': total_orders,
            'turnover': turnover,
            'state_data': state_data,
            'orders': order_details,
            'current_date': timezone.now().strftime('%Y-%m-%d'),
        }
        
        log_action(request.user, supplier, 'impression')  # Log impression
        html_string = render_to_string('pharmacy_supplier_order_history_pdf.html', context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="pharmacy_order_history_{supplier.name.replace(" ", "_")}.pdf"'
        HTML(string=html_string).write_pdf(response)
        return response
    except Exception as e:
        return HttpResponse(f"Erreur lors de la génération du PDF : {str(e)}", status=500)
# Dashboard main view
def pharmacy_dashboard(request):
    """Render the pharmacy dashboard with summary statistics."""
    # Total orders
    total_orders = PharmacyOrder.objects.count()
    
    # Total suppliers
    total_suppliers = PharmacySupplier.objects.count()
    
    # Total order amount (sum of amount_total)
    total_order_amount = PharmacyOrder.objects.aggregate(total=Sum('amount_total'))['total'] or 0.0
    
    # Get all orders for the table
    orders = PharmacyOrder.objects.select_related('supplier', 'currency').order_by('-date_order')[:5]  # Limit to 5 recent orders
    
    # Get all suppliers for the filter dropdown
    suppliers = PharmacySupplier.objects.all()
    
    # Get order states for the filter dropdown
    purchase_order_states = PharmacyOrder.STATE_CHOICES
    
    context = {
        'total_orders': total_orders,
        'total_suppliers': total_suppliers,
        'total_order_amount': float(total_order_amount),
        'orders': orders,
        'suppliers': suppliers,
        'purchase_order_states': purchase_order_states,
        'page_title': 'Tableau de bord Pharmacie',
    }
    
    return render(request, 'pharmacy_dashboard.html', context)

# Orders evolution chart data
@require_GET
def pharmacy_orders_evolution(request):
    """Provide JSON data for the orders evolution chart."""
    try:
        # Aggregate orders by month
        orders_by_month = (
            PharmacyOrder.objects
            .annotate(month=TruncMonth('date_order'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        
        labels = [entry['month'].strftime('%Y-%m') if entry['month'] else 'N/A' for entry in orders_by_month]
        data = [entry['count'] for entry in orders_by_month]
        
        return JsonResponse({
            'labels': labels,
            'data': data,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Orders by state chart data
@require_GET
def pharmacy_orders_by_state(request):
    """Provide JSON data for the orders by state chart."""
    try:
        # Aggregate orders by state
        orders_by_state = (
            PharmacyOrder.objects
            .values('state')
            .annotate(count=Count('id'))
            .order_by('state')
        )
        
        labels = [dict(PharmacyOrder.STATE_CHOICES).get(entry['state'], entry['state']) for entry in orders_by_state]
        data = [entry['count'] for entry in orders_by_state]
        
        return JsonResponse({
            'labels': labels,
            'data': data,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Filtered orders list
@require_POST
def pharmacy_order_list_filtered(request):
    """Provide filtered orders list for the dashboard."""
    try:
        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')
        supplier = request.POST.get('supplier', '')
        status = request.POST.get('status', '')
        
        orders = PharmacyOrder.objects.select_related('supplier', 'currency').order_by('-date_order')
        
        if start_date:
            orders = orders.filter(date_order__gte=start_date)
        if end_date:
            orders = orders.filter(date_order__lte=end_date)
        if supplier:
            orders = orders.filter(supplier_id=supplier)
        if status:
            orders = orders.filter(state=status)
        
        orders_data = [{
            'id': order.id,
            'name': order.name,
            'supplier_name': order.supplier.name if order.supplier else '',
            'date_order': order.date_order.strftime('%Y-%m-%d') if order.date_order else '',
            'amount_total': float(order.amount_total) if order.amount_total else 0,
            'state': order.state,
            'state_display': order.get_state_display(),
            'currency': order.currency.libelle if order.currency else 'MAD',
        } for order in orders]
        
        return JsonResponse({'orders': orders_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
