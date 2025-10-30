from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
import json
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template, render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from apps.home.utils import log_action
from django.core.paginator import Paginator

from django.db import transaction, IntegrityError
from django.db.models import ProtectedError, Max, Sum, Q, F, ExpressionWrapper, DecimalField
try:
    from weasyprint import HTML, CSS
except Exception:
    HTML = None
    CSS = None
from decimal import Decimal
import json
import logging
import datetime

from .models.product import Product
from .models.category import Category
from .models.unit_of_mesure import UnitOfMesure
from .models.stock_location import StockLocation
from .models.location_type import LocationType
from .models.product_type import ProductType
from .models.operation_type import OperationType
from .models.stock_move import StockMove
from .models.line_stock_move import LineStockMove
from .models.product_location import ProductLocation
from .models.product_departement import InventoryProductDepartment
from apps.hr.models import Department
from apps.purchases.models import  Supplier, PurchaseOrder, PurchaseOrderLine

from .forms import CategoryForm
from .forms import UnitOfMesureForm
from .forms import LocationTypeForm
from .forms import StockLocationForm
from .forms import ProductTypeForm
from .forms import OperationTypeForm
from .forms import StockMoveForm
from .forms import ProductLocationForm
from .forms import ProductForm

# ---------------------------------PRODUCT ------------------------------------------------------------------
# Display list of products
def product_list(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    sort_by = request.GET.get('sort_by', 'product_id')
    sort_order = request.GET.get('sort_order', 'desc')
    
    # Mapping columns for sorting
    sort_mapping = {
        'default_code': 'default_code',
        'name': 'name',
        'category': 'categ__label',
        'standard_price': 'standard_price',
        'stock_minimal': 'stock_minimal',
        'uom': 'uom__symbole',
        'total_quantity': 'total_quantity_cached',
        'product_id': 'product_id'
    }
    
    # Validate the sort field
    sort_field = sort_mapping.get(sort_by, 'product_id')
    order_prefix = '-' if sort_order == 'desc' else ''
    
    products = Product.objects.all().order_by(f'{order_prefix}{sort_field}')
    
    # Filter by category if provided
    if category:
        products = products.filter(categ__label=category)
    
    # Search by multiple fields
    if query:
        # Normaliser la requête pour gérer les séparateurs décimaux
        normalized_query = query.replace(',', '.')
        
        products = products.filter(
            Q(name__icontains=query) |
            Q(default_code__icontains=query) |
            Q(categ__label__icontains=query) |
            Q(standard_price__icontains=normalized_query) |
            Q(stock_minimal__icontains=query) |
            Q(uom__symbole__icontains=query) |  
            Q(uom__label__icontains=query) |    
            Q(total_quantity_cached__icontains=normalized_query)
        )
    
    paginator = Paginator(products, 5)
    page_number = request.GET.get('page')
    if (query or category) and not page_number:
        page_number = 1
    page_obj = paginator.get_page(page_number)
    
    # Get all categories for the filter
    categories = Category.objects.all().order_by('label')
    
    locations = StockLocation.objects.select_related('location_type', 'parent_location').all()
    form = ProductForm()
    product_locations_json = {}
    for product in page_obj:
        product_locations = list(ProductLocation.objects.filter(product=product).values('location', 'quantity_stored'))
        for loc in product_locations:
            loc['location_id'] = loc.pop('location')  
            loc['quantity_stored'] = float(loc['quantity_stored'])
        product_locations_json[product.pk] = json.dumps(product_locations) if product_locations else '[]'
    
    # Retrieve session messages and clear them immediately
    swal_success = None
    swal_error = None
    
    # Check if we came from a redirect with messages
    if 'swal_success' in request.session:
        swal_success = request.session.pop('swal_success')
    if 'swal_error' in request.session:
        swal_error = request.session.pop('swal_error')
    
    return render(request, 'products.html', {
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'form': form,
        'page_title': 'Produits',
        'product': None,
        'locations': locations,
        'product_locations': json.dumps([]),
        'product_locations_json': product_locations_json,
        'categories': categories,
        'current_category': category,
        'search': query,
        'sort_by': sort_by,
        'sort_order': sort_order,
        'swal_success': swal_success,
        'swal_error': swal_error,
    })

# Generate product reference
def generate_product_reference():
    last_product = Product.objects.filter(default_code__startswith='PDT-').order_by('-product_id').first()
    if last_product and last_product.default_code:
        try:
            last_number = int(last_product.default_code.split('-')[-1])
        except ValueError:
            last_number = 0
    else:
        last_number = 0
    return f'PDT-{last_number + 1:04d}'

# Create product
@csrf_exempt
@transaction.atomic
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            stockable_type, _ = ProductType.objects.get_or_create(label='stockable')
            product.product_type = stockable_type
            product.default_code = generate_product_reference()
            product.save()
            log_action(request.user, product, 'creation')
            ProductLocation.objects.filter(product=product).delete()
            locations_json = request.POST.get('locations_json', '[]')
            try:
                locations = json.loads(locations_json)
            except json.JSONDecodeError:
                request.session['swal_error'] = 'Erreur dans les données des emplacements.'
                return redirect('product_list')
            total = 0
            for loc in locations:
                location_id = loc.get('location_id')
                quantity_stored = loc.get('quantity_stored')
                if location_id and quantity_stored:
                    try:
                        location = StockLocation.objects.get(pk=location_id)
                        quantity = float(quantity_stored)
                        if quantity <= 0:
                            raise ValueError("La quantité doit être supérieure à 0.")
                        ProductLocation.objects.create(
                            product=product,
                            location=location,
                            quantity_stored=quantity,
                            last_count_date=timezone.now().date()
                        )
                        log_action(request.user, product, 'creation')
                        total += quantity
                    except (StockLocation.DoesNotExist, ValueError) as e:
                        request.session['swal_error'] = f"Emplacement {location_id} invalide ou quantité incorrecte: {str(e)}"
                        return redirect('product_list')
            product.total_quantity_cached = total
            product.save()
            log_action(request.user, product, 'creation')
            request.session['swal_success'] = 'Produit créé avec succès !'
            return redirect('product_list')
        else:
            request.session['swal_error'] = 'Erreur dans le formulaire produit.'
            return redirect('product_list')
    else:
        # GET
        form = ProductForm()
        products = Product.objects.all().order_by('-product_id')
        paginator = Paginator(products, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        product_locations_json = {}
        for product in page_obj:
            product_locations = list(ProductLocation.objects.filter(product=product).values('location', 'quantity_stored'))
            for loc in product_locations:
                loc['location_id'] = loc.pop('location')  
                loc['quantity_stored'] = float(loc['quantity_stored'])
            product_locations_json[product.pk] = json.dumps(product_locations) if product_locations else '[]'
        return render(request, 'products.html', {
            'form': form,
            'page_title': 'Ajouter un Produit',
            'product': None,
            'locations': StockLocation.objects.select_related('location_type', 'parent_location').all(),
            'product_locations': json.dumps([]),
            'product_locations_json': product_locations_json,
            'products': products,
            'page_obj': paginator.get_page(page_number),
        })

@csrf_exempt
@transaction.atomic
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            
            # Handle manual image deletion
            if request.POST.get('clear_image'):
                product.image_1920.delete(save=False)
                product.image_1920 = None
            
            if not product.product_type:
                stockable_type, _ = ProductType.objects.get_or_create(label='stockable')
                product.product_type = stockable_type
            product.save()
            log_action(request.user, product, 'modification')
            locations_json = request.POST.get('locations_json', '[]')
            try:
                locations = json.loads(locations_json)
            except json.JSONDecodeError:
                request.session['swal_error'] = 'Erreur dans les données des emplacements.'
                return redirect('product_list')
            
            # Traiter les emplacements
            ProductLocation.objects.filter(product=product).delete()  
            total = 0
            
            if locations and len(locations) > 0:
                for loc in locations:
                    location_id = loc.get('location_id')
                    quantity_stored = loc.get('quantity_stored')
                    if location_id and quantity_stored is not None:  
                        try:
                            location = StockLocation.objects.get(pk=location_id)
                            quantity = float(quantity_stored)
                            if quantity < 0:
                                raise ValueError("La quantité ne peut pas être négative.")
                            ProductLocation.objects.create(
                                product=product,
                                location=location,
                                quantity_stored=quantity,
                                last_count_date=timezone.now().date()
                            )
                            log_action(request.user, product, 'creation')
                            total += quantity
                        except (StockLocation.DoesNotExist, ValueError) as e:
                            request.session['swal_error'] = f"Emplacement {location_id} invalide ou quantité incorrecte: {str(e)}"
                            return redirect('product_list')
            
            product.total_quantity_cached = total
            product.save()
            log_action(request.user, product, 'modification')
            request.session['swal_success'] = 'Produit et emplacements modifiés avec succès !'
            return redirect('product_list')
        else:
            request.session['swal_error'] = 'Erreur dans le formulaire produit.'
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    product_locations = list(ProductLocation.objects.filter(product=product).values('location', 'quantity_stored'))
    for loc in product_locations:
        loc['location_id'] = loc.pop('location')  
        loc['quantity_stored'] = float(loc['quantity_stored'])
    product_locations_json = json.dumps(product_locations, ensure_ascii=False) if product_locations else '[]'
    products = Product.objects.all().order_by('-product_id')
    product_locations_dict = {}
    for p in products:
        locs = list(ProductLocation.objects.filter(product=p).values('location_id', 'quantity_stored'))
        for loc in locs:
            loc['quantity_stored'] = float(loc['quantity_stored'])
        product_locations_dict[p.pk] = json.dumps(locs)
    paginator = Paginator(products, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'products.html', {
        'form': form,
        'page_title': 'Modifier un Produit',
        'product': product,
        'locations': StockLocation.objects.select_related('location_type', 'parent_location').all(),
        'categories': Category.objects.all().order_by('label'),
        'product_locations': product_locations_json,
        'products': products,
        'page_obj': page_obj,
        'product_locations_json': product_locations_dict,
        'swal_success': None,
        'swal_error': None,
    })

# Delete a product
@csrf_exempt
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        try:
            product.delete()
            log_action(request.user, product, 'suppression')
            request.session['swal_success'] = 'Produit supprimé avec succès !'
        except Exception as e:
            request.session['swal_error'] = f'Erreur lors de la suppression du produit: {str(e)}'
        return redirect('product_list')
    return redirect('product_list')


@csrf_exempt
def product_export(request):
    return redirect('product_list')

# Product list ajax
def product_list_ajax(request):
    query = request.GET.get('q', '')
    products = Product.objects.all().order_by('-product_id')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(default_code__icontains=query) |
            Q(barcode__icontains=query) |
            Q(categ__label__icontains=query) |
            Q(uom__label__icontains=query) |
            Q(standard_price__icontains=query) |
            Q(stock_minimal__icontains=query)
        )
    paginator = Paginator(products, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    html = render_to_string('product_table_body.html', {'page_obj': page_obj, 'product_locations_json': {}})
    return JsonResponse({'html': html})

# --------------------------------CONFIGURATION--------------------------------------------------------
# Tabs display
def configuration(request):
    # unit of mesure
    uom_list = UnitOfMesure.objects.all().order_by('label')
    uom_search = request.GET.get('uom_search', '')
    if uom_search:
        uom_list = uom_list.filter(label__icontains=uom_search) | uom_list.filter(symbole__icontains=uom_search)
    uom_page_number = request.GET.get('uom_page')
    uom_paginator = Paginator(uom_list, 5)
    uoms = uom_paginator.get_page(uom_page_number)

    # Category
    category_list = Category.objects.all().order_by('label')
    category_search = request.GET.get('category_search', '')
    if category_search:
        category_list = category_list.filter(label__icontains=category_search) | category_list.filter(description__icontains=category_search)
    category_page_number = request.GET.get('category_page')
    category_paginator = Paginator(category_list, 5)
    categories = category_paginator.get_page(category_page_number)

    # Product Type
    product_type_list = ProductType.objects.all().order_by('label')
    product_type_search = request.GET.get('product_type_search', '')
    if product_type_search:
        product_type_list = product_type_list.filter(label__icontains=product_type_search)
    product_type_paginator = Paginator(product_type_list, 5)
    product_type_page_number = request.GET.get('product_type_page')
    product_types = product_type_paginator.get_page(product_type_page_number)

    # Operation Type
    operation_type_list = OperationType.objects.all().order_by('label')
    operation_type_search = request.GET.get('operation_type_search', '')
    if operation_type_search:
        operation_type_list = operation_type_list.filter(label__icontains=operation_type_search)
    operation_type_paginator = Paginator(operation_type_list, 5)
    operation_type_page_number = request.GET.get('operation_type_page')
    operation_types = operation_type_paginator.get_page(operation_type_page_number)

    # Location Type
    location_types_list = LocationType.objects.all().order_by('label')
    location_type_search = request.GET.get('location_type_search', '')
    if location_type_search:
        location_types_list = location_types_list.filter(label__icontains=location_type_search) | location_types_list.filter(description__icontains=location_type_search)
    location_type_page_number = request.GET.get('location_type_page')
    location_type_paginator = Paginator(location_types_list, 5)
    location_types_paginated = location_type_paginator.get_page(location_type_page_number)

    # Location
    location_list = StockLocation.objects.select_related('location_type', 'parent_location').all().order_by('name')
    location_search = request.GET.get('location_search', '')
    if location_search:
        location_list = location_list.filter(name__icontains=location_search) | location_list.filter(location_type__label__icontains=location_search)
    location_page_number = request.GET.get('location_page')
    location_paginator = Paginator(location_list, 5)
    locations = location_paginator.get_page(location_page_number)
    location_parents = StockLocation.objects.all()

    uom_form = UnitOfMesureForm()
    category_form = CategoryForm()
    product_type_form = ProductTypeForm()
    operation_type_form = OperationTypeForm()
    location_type_form = LocationTypeForm()
    location_form = StockLocationForm()

    return render(request, 'configuration/configuration.html', {
        'uoms': uoms,
        'categories': categories,
        'product_types': product_types,
        'product_type_list': product_type_list,
        'operation_types': operation_types,
        'operation_type_list': operation_type_list,
        'uom_form': uom_form,
        'category_form': category_form,
        'product_type_form': product_type_form,
        'operation_type_form': operation_type_form,
        'locations': locations,
        'location_form': location_form,
        'location_parents': location_parents,
        'location_types_paginated': location_types_paginated,
        'location_type_form': location_type_form,
        'location_types': location_types_list,
        'page_title': 'Configuration',
    })

# --- UOM CRUD ---
@csrf_exempt
def uom_create(request):
    if request.method == 'POST':
        form = UnitOfMesureForm(request.POST)
        if form.is_valid():
            form.save()
            log_action(request.user, form.instance, 'creation')
            return JsonResponse({'success': True, 'message': 'Unité de mesure créée avec succès.'})
        return JsonResponse({'success': False, 'errors': form.errors})

@require_GET
def uom_search(request):
    query = request.GET.get('q', '')
    uoms = UnitOfMesure.objects.all().order_by('label')
    if query:
        uoms = uoms.filter(label__icontains=query) | uoms.filter(symbole__icontains=query)
    
    html = render_to_string('configuration/partials/uom_table_body.html', {'uoms': uoms})
    return HttpResponse(html)

@csrf_exempt
def uom_update(request, pk):
    uom = get_object_or_404(UnitOfMesure, pk=pk)
    if request.method == 'POST':
        form = UnitOfMesureForm(request.POST, instance=uom)
        if form.is_valid():
            form.save()
            log_action(request.user, form.instance, 'modification')
            return JsonResponse({'success': True, 'message': 'Unité de mesure modifiée avec succès.'})
        return JsonResponse({'success': False, 'errors': form.errors})

@csrf_exempt
def uom_delete(request, pk):
    try:
        uom = UnitOfMesure.objects.get(pk=pk)
        uom.delete()
        log_action(request.user, uom, 'suppression')
        return JsonResponse({'success': True, 'message': 'Unité de mesure supprimée avec succès.'})
    except ProtectedError:
        return JsonResponse({'success': False, 'error': "Cette unité est utilisée par des produits."})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# --- Category CRUD ---
@csrf_exempt
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            log_action(request.user, form.instance, 'creation')
            return JsonResponse({'success': True, 'message': 'Catégorie créée avec succès.'})
        return JsonResponse({'success': False, 'errors': form.errors})

@require_GET
def category_search(request):
    query = request.GET.get('q', '')
    categories = Category.objects.all().order_by('label')
    if query:
        categories = categories.filter(label__icontains=query) | categories.filter(description__icontains=query)
    
    html = render_to_string('configuration/partials/category_table_body.html', {'categories': categories})
    return HttpResponse(html)

@csrf_exempt
def category_update(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            log_action(request.user, form.instance, 'modification')
            return JsonResponse({'success': True, 'message': 'Catégorie modifiée avec succès.'})
        return JsonResponse({'success': False, 'errors': form.errors})

@csrf_exempt
def category_delete(request, pk):
    try:
        cat = Category.objects.get(pk=pk)
        cat.delete()
        log_action(request.user, cat, 'suppression')
        return JsonResponse({'success': True, 'message': 'Catégorie supprimée avec succès.'})
    except ProtectedError:
        return JsonResponse({'success': False, 'error': "Cette catégorie est utilisée par des produits."})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# --- Location CRUD ---
@csrf_exempt
def location_create(request):
    if request.method == 'POST':
        form = StockLocationForm(request.POST)
        if form.is_valid():
            loc = form.save()
            log_action(request.user, loc, 'creation')
            return JsonResponse({'success': True, 'message': 'Emplacement créé avec succès.'})
        return JsonResponse({'success': False, 'errors': form.errors})

@require_GET
def location_search(request):
    query = request.GET.get('q', '')
    locations = StockLocation.objects.select_related('location_type', 'parent_location').all().order_by('name')
    if query:
        locations = locations.filter(name__icontains=query) | locations.filter(location_type__label__icontains=query) | locations.filter(parent_location__name__icontains=query)
    
    html = render_to_string('configuration/partials/location_table_body.html', {'locations': locations})
    return HttpResponse(html)

@csrf_exempt
def location_update(request, pk):
    loc = get_object_or_404(StockLocation, pk=pk)
    if request.method == 'POST':
        form = StockLocationForm(request.POST, instance=loc)
        if form.is_valid():
            form.save()
            log_action(request.user, form.instance, 'modification')
            return JsonResponse({'success': True, 'message': 'Emplacement modifié avec succès.'})
        return JsonResponse({'success': False, 'errors': form.errors})

@csrf_exempt
def location_delete(request, pk):
    try:
        loc = StockLocation.objects.get(pk=pk)
        loc.delete()
        log_action(request.user, loc, 'suppression')
        return JsonResponse({'success': True, 'message': 'Emplacement supprimé avec succès.'})
    except ProtectedError:
        return JsonResponse({'success': False, 'error': "Cet emplacement est utilisé par un produit ou comme parent d'un autre emplacement."})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# --- Location Type CRUD ---
@csrf_exempt
def location_type_list_json(request):
    types = LocationType.objects.all().order_by('label')
    data = [{"id": t.location_type_id, "label": t.label} for t in types]
    return JsonResponse({"types": data})

@require_GET
def location_type_search(request):
    query = request.GET.get('q', '')
    location_types = LocationType.objects.all().order_by('label')
    if query:
        location_types = location_types.filter(label__icontains=query) | location_types.filter(description__icontains=query)
    
    html = render_to_string('configuration/partials/location_type_table_body.html', {'location_types_paginated': location_types})
    return HttpResponse(html)
    
@csrf_exempt
def location_type_create(request):
    if request.method == 'POST':
        form = LocationTypeForm(request.POST)
        if form.is_valid():
            obj = form.save()
            log_action(request.user, obj, 'creation')
            return JsonResponse({'success': True, 'message': 'Type d\'emplacement créé avec succès.', 'id': obj.location_type_id})
        return JsonResponse({'success': False, 'errors': form.errors})

@csrf_exempt
def location_type_update(request, pk):
    obj = get_object_or_404(LocationType, pk=pk)
    if request.method == 'POST':
        form = LocationTypeForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            log_action(request.user, form.instance, 'modification')
            return JsonResponse({'success': True, 'message': 'Type d\'emplacement modifié avec succès.'})
        return JsonResponse({'success': False, 'errors': form.errors})

@csrf_exempt
def location_type_delete(request, pk):
    try:
        obj = LocationType.objects.get(pk=pk)
        obj.delete()
        log_action(request.user, obj, 'suppression')
        return JsonResponse({'success': True, 'message': 'Type d\'emplacement supprimé avec succès.'})
    except ProtectedError:
        return JsonResponse({'success': False, 'error': "Ce type d'emplacement est utilisé par au moins un emplacement."})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# --- Product Type CRUD ---
@csrf_exempt
def product_type_create(request):
    if request.method == 'POST':
        form = ProductTypeForm(request.POST)
        if form.is_valid():
            form.save()
            log_action(request.user, form.instance, 'creation')
            return JsonResponse({'success': True, 'message': 'Type de produit créé avec succès.'})
        return JsonResponse({'success': False, 'errors': form.errors})

@require_GET
def product_type_search(request):
    query = request.GET.get('q', '')
    product_types = ProductType.objects.all().order_by('label')
    if query:
        product_types = product_types.filter(label__icontains=query)
    
    html = render_to_string('configuration/partials/product_type_table_body.html', {'product_types': product_types})
    return HttpResponse(html)

@csrf_exempt
def product_type_update(request, pk):
    obj = get_object_or_404(ProductType, pk=pk)
    if request.method == 'POST':
        form = ProductTypeForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            log_action(request.user, form.instance, 'modification')
            return JsonResponse({'success': True, 'message': 'Type de produit modifié avec succès.'})
        return JsonResponse({'success': False, 'errors': form.errors})

@csrf_exempt
def product_type_delete(request, pk):
    try:
        obj = ProductType.objects.get(pk=pk)
        obj.delete()
        log_action(request.user, obj, 'suppression')
        return JsonResponse({'success': True, 'message': 'Type de produit supprimé avec succès.'})
    except ProtectedError:
        return JsonResponse({'success': False, 'error': "Ce type est utilisé par des produits."})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# --- Operation Type CRUD ---
@csrf_exempt
def operation_type_create(request):
    if request.method == 'POST':
        form = OperationTypeForm(request.POST)
        if form.is_valid():
            form.save()
            log_action(request.user, form.instance, 'creation')
            return JsonResponse({'success': True, 'message': 'Type d\'opération créé avec succès.'})
        return JsonResponse({'success': False, 'errors': form.errors})

@require_GET
def operation_type_search(request):
    query = request.GET.get('q', '')
    operation_types = OperationType.objects.all().order_by('label')
    if query:
        operation_types = operation_types.filter(label__icontains=query)
    
    html = render_to_string('configuration/partials/operation_type_table_body.html', {'operation_types': operation_types})
    return HttpResponse(html)

@csrf_exempt
def operation_type_update(request, pk):
    obj = get_object_or_404(OperationType, pk=pk)
    if request.method == 'POST':
        form = OperationTypeForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            log_action(request.user, form.instance, 'modification')
            return JsonResponse({'success': True, 'message': 'Type d\'opération modifié avec succès.'})
        return JsonResponse({'success': False, 'errors': form.errors})

@csrf_exempt
def operation_type_delete(request, pk):
    try:
        obj = OperationType.objects.get(pk=pk)
        obj.delete()
        log_action(request.user, obj, 'suppression')
        return JsonResponse({'success': True, 'message': 'Type d\'opération supprimé avec succès.'})
    except ProtectedError:
        return JsonResponse({'success': False, 'error': "Ce type est utilisé par des opérations."})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# ------------------------------------ PRODUCT LOCATION --------------------------------------------------------------
# List
def product_location_list(request):
    qs = ProductLocation.objects.select_related('product', 'location').order_by('-pl_id')
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'product_location_list.html', {
        'page_obj': page_obj,
        'page_title': 'Produit / Emplacement',
    })

# --- Product Location CRUD ---
@transaction.atomic
def product_location_create(request):
    if request.method == 'POST':
        form = ProductLocationForm(request.POST)
        if form.is_valid():
            form.save()
            log_action(request.user, form.instance, 'creation')
            return redirect('product_location_list')
    else:
        form = ProductLocationForm()
    return render(request, 'product_location_form.html', {
        'form': form,
        'page_title': 'Ajouter Produit / Emplacement',
    })

@transaction.atomic
def product_location_update(request, pk):
    pl = get_object_or_404(ProductLocation, pk=pk)
    if request.method == 'POST':
        form = ProductLocationForm(request.POST, instance=pl)
        if form.is_valid():
            form.save()
            log_action(request.user, form.instance, 'modification')
            return redirect('product_location_list')
    else:
        form = ProductLocationForm(instance=pl)
    return render(request, 'product_location_form.html', {
        'form': form,
        'page_title': 'Modifier Produit / Emplacement',
    })

@transaction.atomic
def product_location_delete(request, pk):
    pl = get_object_or_404(ProductLocation, pk=pk)
    if request.method == 'POST':
        pl.delete()
        log_action(request.user, pl, 'suppression')
        return redirect('product_location_list')
    return render(request, 'confirm_delete.html', {
        'object': pl,
        'page_title': 'Supprimer Produit / Emplacement',
        'cancel_url': 'product_location_list',
    })

# ------------------------------------------------- STOCK MOVE -----------------------------------------------
# Generate reference move auto
def _get_next_reference():
    last_id = StockMove.objects.aggregate(max_id=Max('move_id'))['max_id'] or 0
    return f'SM-{last_id + 1:04d}'

# List
def stock_move_list(request):
    sort_by = request.GET.get('sort_by', 'date_created')
    sort_order = request.GET.get('sort_order', 'desc')

    sort_mapping = {
        'reference': 'reference',
        'operation_type': 'operation_type__label',
        'source_location': 'source_location__name',
        'dest_location': 'dest_location__name',
        'department': 'department__name',
        'supplier': 'supplier__name',
        'state': 'state',
        'date_created': 'date_created',
    }

    sort_field = sort_mapping.get(sort_by, 'date_created')
    order_prefix = '-' if sort_order == 'desc' else ''
    
    moves = StockMove.objects.select_related(
        'operation_type', 'source_location', 'dest_location',
        'department', 'supplier', 'created_by'
    ).prefetch_related('lines__product', 'lines__uom').order_by(f'{order_prefix}{sort_field}')

    state = request.GET.get('state', '')
    if state:
        moves = moves.filter(state=state)

    operation_type = request.GET.get('operation_type', '')
    if operation_type:
        moves = moves.filter(operation_type__label=operation_type)

    search = request.GET.get('search', '')
    if search:
        moves = moves.filter(
            Q(reference__icontains=search) |
            Q(scheduled_date__icontains=search) |
            Q(source_location__name__icontains=search) |
            Q(dest_location__name__icontains=search) |
            Q(department__name__icontains=search) |
            Q(supplier__name__icontains=search)
        )

    paginator = Paginator(moves, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    operation_types = OperationType.objects.all().order_by('label')

    swal_success = request.session.pop('swal_success', None)
    swal_error = request.session.pop('swal_error', None)

    return render(request, 'stock_move_list.html', {
        'page_obj': page_obj,
        'page_title': 'Mouvements de Stock',
        'states': StockMove.STATE_CHOICES,
        'current_state': state,
        'current_operation_type': operation_type,
        'operation_types': operation_types,
        'search': search,
        'sort_by': sort_by,
        'sort_order': sort_order,
        'swal_success': swal_success,
        'swal_error': swal_error,
    })

# Stock move form
def _render_stock_move_form(request, move_form, move_lines, move=None, edit=False):
    products = Product.objects.select_related('uom').all()
    uoms = UnitOfMesure.objects.all()
    product_locations = ProductLocation.objects.all()
    stock_by_product_location = {
        f"{pl.product.pk}_{pl.location.pk}": float(pl.quantity_stored or 0)
        for pl in product_locations
    }
    return render(request, 'stock_move_form.html', {
        'move_form': move_form,
        'page_title': 'Éditer un Mouvement' if edit else 'Créer un Mouvement',
        'move': move,
        'products': products,
        'uoms': uoms,
        'departments': Department.objects.all(),
        'suppliers': Supplier.objects.all(),
        'move_lines': move_lines,
        'stock_by_product_location': stock_by_product_location,
    })

# ---
def get_default_operation_type_id():
    op = OperationType.objects.filter(label__icontains="transfert interne").first()
    return op.pk if op else None
# ---

def get_available_qty(product_id, location_id):
    pl = ProductLocation.objects.filter(product_id=product_id, location_id=location_id).first()
    return float(pl.quantity_stored) if pl else 0

def get_supplier_orders(request):
    supplier_id = request.GET.get('supplier_id')

    orders = PurchaseOrder.objects.filter(partner_id=supplier_id, state='confirmed')
    data = {
        "orders": [{"id": o.id, "name": o.name} for o in orders]
    }
    return JsonResponse(data)

def get_order_lines(request):
    order_id = request.GET.get('order_id')
    if not order_id:
        return JsonResponse({"lines": []})
    try:
        lines = PurchaseOrderLine.objects.filter(order_id=order_id)
        data = {
            "lines": [{
                "product_id": l.product_id,
                "product_qty": float(l.product_qty),
                "product_uom_id": l.product_uom_id
            } for l in lines]
        }
        return JsonResponse(data)
    except Exception as e:
        logging.exception("Erreur dans get_order_lines")
        return JsonResponse({"lines": [], "error": str(e)}, status=500)

# Add a stock move
@transaction.atomic
def stock_move_create(request):
    if request.method == 'POST':
        move_form = StockMoveForm(request.POST)
        try:
            lines = json.loads(request.POST.get('lines_json', '[]'))
        except Exception:
            lines = []
        operation_type = None
        operation_label = ''
        if move_form.is_valid():
            operation_type = move_form.cleaned_data.get('operation_type')
            operation_label = operation_type.label.lower() if operation_type else ''
        validation_errors = []
        if not lines or not any(l.get('product') and float(l.get('quantity_demanded', 0)) > 0 for l in lines):
            move_form.add_error(None, "Vous devez ajouter au moins une ligne de produit avec une quantité demandée.")
            move_lines = []
            for l in lines:
                move_lines.append({
                    "product_id": int(l.get("product") or l.get("product_id") or 0),
                    "quantity_demanded": l.get("quantity_demanded", ""),
                    "uom_id": int(l.get("uom") or l.get("uom_id") or 0),
                    "quantity_arrived": l.get("quantity_arrived", ""),
                })
            return _render_stock_move_form(request, move_form, move_lines)

        for l in lines:
            product_id = l.get('product')
            qty_demanded = Decimal(str(l.get('quantity_demanded', 0)))
            qa_raw = l.get('quantity_arrived', 0)
            quantity_arrived = Decimal(str(qa_raw)) if str(qa_raw).strip() else Decimal('0')
            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                validation_errors.append(f"Produit : {product_id} n'existe pas.")
                continue
            if 'transfert' in operation_label or 'consommation' in operation_label or 'réception' in operation_label:
                source_location = move_form.cleaned_data.get('source_location')
                if source_location:
                    pl_src = ProductLocation.objects.filter(
                        product_id=product_id,
                        location=source_location
                    ).first()
                    if not pl_src:
                        validation_errors.append(f"Le produit {product.name} n'existe pas dans l'emplacement d'origine.")
                        continue
                    if qty_demanded > pl_src.quantity_stored:
                        validation_errors.append(
                            f"Produit {product.name}: Quantité demandée ({qty_demanded}) "
                            f"supérieure au stock disponible dans l'emplacement ({pl_src.quantity_stored})"
                        )
                        continue
                    if quantity_arrived > 0 and quantity_arrived > pl_src.quantity_stored:
                        validation_errors.append(
                            f"Produit {product.name}: Quantité arrivée ({quantity_arrived}) "
                            f"supérieure au stock disponible dans l'emplacement ({pl_src.quantity_stored})"
                        )

        if validation_errors:
            for error in validation_errors:
                move_form.add_error(None, error)
            move_lines = []
            for l in lines:
                move_lines.append({
                    "product_id": int(l.get("product") or l.get("product_id") or 0),
                    "quantity_demanded": l.get("quantity_demanded", ""),
                    "uom_id": int(l.get("uom") or l.get("uom_id") or 0),
                    "quantity_arrived": l.get("quantity_arrived", ""),
                })
            return _render_stock_move_form(request, move_form, move_lines)
        if move_form.is_valid():
            move = move_form.save(commit=False)

            if not move.reference:
                move.reference = _get_next_reference()

            if 'consommation' in operation_label:
                move.department_id = request.POST.get('department') or None
                move.dest_location = None
                move.supplier = None
            elif 'réception' in operation_label:
                supplier_id = request.POST.get('supplier')
                if supplier_id:
                    try:
                        move.supplier = Supplier.objects.get(pk=int(supplier_id))
                    except Supplier.DoesNotExist:
                        move.supplier = None
                else:
                    move.supplier = None
                move.department = None
            else:
                move.department = None
                move.supplier = None

            action = request.POST.get('action', 'save')
            if action != 'save':
                move.state = {
                    'confirm': 'confirmed',
                    'done': 'done',
                    'cancel': 'canceled',
                }.get(action, 'draft')
            move.save()
            log_action(request.user, move, 'creation')
            LineStockMove.objects.filter(move=move).delete()
            for l in lines:
                if l.get('product') and l.get('quantity_demanded') and l.get('uom'):
                    LineStockMove.objects.create(
                        move=move,
                        product_id=int(l['product']),
                        quantity_demanded=l['quantity_demanded'],
                        uom_id=l['uom'],
                        quantity_arrived=l.get('quantity_arrived', 0)
                    )

            if action == 'done':
                for l in lines:
                    product_id = int(l['product'])
                    qty_demanded = Decimal(str(l.get('quantity_demanded', 0)))
                    qty_arrived = Decimal(str(l.get('quantity_arrived', 0))) if l.get('quantity_arrived') else qty_demanded
                    src = move.source_location
                    dest = move.dest_location
                    if 'transfert' in operation_label:
                        # Source : on retire la quantité DEMANDÉE
                        if src:
                            pl_src = ProductLocation.objects.filter(product_id=product_id, location=src).first()
                            if pl_src:
                                pl_src.quantity_stored = max(Decimal('0'), pl_src.quantity_stored - qty_demanded)
                                pl_src.save()
                        # Destination : on ajoute la quantité ARRIVÉE
                        if dest:
                            pl_dest, _ = ProductLocation.objects.get_or_create(
                                product_id=product_id, location=dest, defaults={'quantity_stored': 0})
                            pl_dest.quantity_stored += qty_arrived
                            pl_dest.save()
                    elif 'consommation' in operation_label:
                        src = move.source_location
                        dept = move.department
                        # Source : on retire la quantité DEMANDÉE
                        if src:
                            pl_src = ProductLocation.objects.filter(product_id=product_id, location=src).first()
                            if pl_src:
                                pl_src.quantity_stored = max(Decimal('0'), pl_src.quantity_stored - qty_demanded)
                                pl_src.save()
                        # Département : on ajoute la quantité ARRIVÉE
                        if dept:
                            ipd, _ = InventoryProductDepartment.objects.get_or_create(
                                product_id=product_id, department=dept, defaults={'quantity_stored': 0})
                            ipd.quantity_stored += qty_arrived
                            ipd.save()
                    elif 'réception' in operation_label:
                        # Destination : on ajoute la quantité ARRIVÉE
                        if dest:
                            pl_dest, _ = ProductLocation.objects.get_or_create(
                                product_id=product_id, location=dest, defaults={'quantity_stored': 0})
                            pl_dest.quantity_stored += qty_arrived
                            pl_dest.save()
                    product = Product.objects.get(pk=product_id)
                    # Le total stock = somme de tous les emplacements (après soustraction de la demandée)
                    total = ProductLocation.objects.filter(product=product).aggregate(total=Sum('quantity_stored'))['total'] or 0
                    product.total_quantity_cached = total
                    product.save(update_fields=['total_quantity_cached'])
                move.effective_date = timezone.now().date()
                move.save()
                log_action(request.user, move, 'modification')
                request.session['swal_success'] = "Mouvement validé avec succès. Les stocks ont été mis à jour."
            elif action == 'save':
                request.session['swal_success'] = "Mouvement sauvegardé avec succès."
            else:
                request.session['swal_success'] = "Mouvement sauvegardé avec succès."
            return redirect('stock_move_list')
        else:
            return _render_stock_move_form(request, move_form, lines)
    else:
        move_form = StockMoveForm()
        return _render_stock_move_form(request, move_form, [])

# Update a stock move
@transaction.atomic
def stock_move_update(request, pk):
    move = get_object_or_404(StockMove, pk=pk)
    if request.method == 'POST':
        move_form = StockMoveForm(request.POST, instance=move)
        try:
            lines = json.loads(request.POST.get('lines_json', '[]'))
        except Exception:
            lines = []
        operation_type = None
        operation_label = ''
        if move_form.is_valid():
            operation_type = move_form.cleaned_data.get('operation_type')
            operation_label = operation_type.label.lower() if operation_type else ''
        validation_errors = []
        for l in lines:
            product_id = int(l.get('product')) if l.get('product') else int(l.get('product_id', 0))
            qty_demanded = Decimal(str(l.get('quantity_demanded', 0)))
            qa_raw = l.get('quantity_arrived', 0)
            quantity_arrived = Decimal(str(qa_raw)) if str(qa_raw).strip() else Decimal('0')
            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                validation_errors.append(f"Produit ID {product_id} n'existe pas.")
                continue
            if 'transfert' in operation_label or 'consommation' in operation_label or 'réception' in operation_label:
                if move_form.cleaned_data.get('source_location'):
                    source_location_id = move_form.cleaned_data['source_location'].pk
                    pl_src = ProductLocation.objects.filter(
                        product_id=product_id,
                        location_id=source_location_id
                    ).first()
                    if not pl_src:
                        validation_errors.append(f"Le produit {product.name} n'existe pas dans l'emplacement d'origine.")
                        continue
                    if qty_demanded > pl_src.quantity_stored:
                        validation_errors.append(
                            f"Produit {product.name}: Quantité demandée ({qty_demanded}) > stock dans l'emplacement ({pl_src.quantity_stored})"
                        )
                        continue
                    if quantity_arrived > 0 and quantity_arrived > pl_src.quantity_stored:
                        validation_errors.append(
                            f"Produit {product.name}: Quantité arrivée ({quantity_arrived}) > stock dans l'emplacement ({pl_src.quantity_stored})"
                        )
        if validation_errors:
            for error in validation_errors:
                move_form.add_error(None, error)
            move_lines = []
            for l in lines:
                move_lines.append({
                    "product_id": int(l.get("product") or l.get("product_id") or 0),
                    "quantity_demanded": l.get("quantity_demanded", ""),
                    "uom_id": int(l.get("uom") or l.get("uom_id") or 0),
                    "quantity_arrived": l.get("quantity_arrived", ""),
                })
            return _render_stock_move_form(request, move_form, move_lines, move=move, edit=True)
        # --- Submit form ---
        if move_form.is_valid():
            move = move_form.save(commit=False)
            if not move.reference:
                move.reference = _get_next_reference()
            if 'consommation' in operation_label:
                department_id = request.POST.get('department')
                move.department_id = department_id if department_id else None
                move.dest_location = None
                move.supplier = None
            elif 'réception' in operation_label:
                supplier_id = request.POST.get('supplier')
                move.supplier_id = int(supplier_id) if supplier_id else None
                move.department = None
            else:
                move.department = None
                move.supplier = None
            action = request.POST.get('action', 'save')
            if action != 'save':
                move.state = {
                    'confirm': 'confirmed',
                    'done': 'done',
                    'cancel': 'canceled'
                }.get(action, 'draft')
            move.save()
            log_action(request.user, move, 'modification')
            LineStockMove.objects.filter(move=move).delete()
            for l in lines:
                if l.get('product') and l.get('quantity_demanded') and l.get('uom'):
                    LineStockMove.objects.create(
                        move=move,
                        product_id=int(l['product']),
                        quantity_demanded=l['quantity_demanded'],
                        uom_id=l['uom'],
                        quantity_arrived=l.get('quantity_arrived', 0)
                    )
            if action == 'done':
                for l in lines:
                    product_id = int(l['product'])
                    qty_demanded = Decimal(str(l.get('quantity_demanded', 0)))
                    qty_arrived = Decimal(str(l.get('quantity_arrived', 0))) if l.get('quantity_arrived') else qty_demanded
                    if 'transfert' in operation_label:
                        src = move.source_location
                        dest = move.dest_location
                        # Source : on retire la quantité DEMANDEE
                        if src:
                            pl_src = ProductLocation.objects.filter(product_id=product_id, location=src).first()
                            if pl_src:
                                pl_src.quantity_stored = max(Decimal('0'), pl_src.quantity_stored - qty_demanded)
                                pl_src.save()
                        # Destination : on ajoute la quantité ARRIVEE
                        if dest:
                            pl_dest, _ = ProductLocation.objects.get_or_create(
                                product_id=product_id, location=dest, defaults={'quantity_stored': 0}
                            )
                            pl_dest.quantity_stored += qty_arrived
                            pl_dest.save()
                    elif 'consommation' in operation_label:
                        src = move.source_location
                        dept = move.department
                        # Source : on retire la quantité DEMANDEE
                        if src:
                            pl_src = ProductLocation.objects.filter(product_id=product_id, location=src).first()
                            if pl_src:
                                pl_src.quantity_stored = max(Decimal('0'), pl_src.quantity_stored - qty_demanded)
                                pl_src.save()
                        # Département : on ajoute la quantité ARRIVEE
                        if dept:
                            ipd, _ = InventoryProductDepartment.objects.get_or_create(
                                product_id=product_id, department=dept, defaults={'quantity_stored': 0}
                            )
                            ipd.quantity_stored += qty_arrived
                            ipd.save()
                    elif 'réception' in operation_label:
                        src = move.source_location
                        dest = move.dest_location
                        # Destination : on ajoute la quantité ARRIVEE
                        if dest:
                            pl_dest, _ = ProductLocation.objects.get_or_create(
                                product_id=product_id, location=dest, defaults={'quantity_stored': 0}
                            )
                            pl_dest.quantity_stored += qty_arrived
                            pl_dest.save()
                    product = Product.objects.get(pk=product_id)
                    # Recalcule le total stock comme somme de tous les emplacements
                    total = ProductLocation.objects.filter(product=product).aggregate(total=Sum('quantity_stored'))['total'] or 0
                    product.total_quantity_cached = total
                    product.save(update_fields=['total_quantity_cached'])
                move.effective_date = timezone.now().date()
                move.save()
                log_action(request.user, move, 'modification')
                request.session['swal_success'] = "Mouvement validé avec succès. Les stocks ont été mis à jour."
            elif action == 'save':
                request.session['swal_success'] = "Mouvement sauvegardé avec succès."
            else:
                request.session['swal_success'] = "Mouvement sauvegardé avec succès."
            return redirect('stock_move_list')
        else:
            return _render_stock_move_form(request, move_form, lines, move=move, edit=True)
    else:
        move_form = StockMoveForm(instance=move)
        move_lines = list(move.lines.values('product_id', 'quantity_demanded', 'uom_id', 'quantity_arrived'))
        return _render_stock_move_form(request, move_form, move_lines, move=move, edit=True)

# Delete a stock move
@transaction.atomic
def stock_move_delete(request, pk):
    move = get_object_or_404(StockMove, pk=pk)
    if request.method == 'POST':
        try:
            move.delete()
            log_action(request.user, move, 'suppression')
            request.session['swal_success'] = f"Mouvement {move.reference} supprimé."
        except IntegrityError as e:
            request.session['swal_error'] = f"Impossible de supprimer : {e}"
        return redirect('stock_move_list')
    return render(request, 'confirm_delete.html', {
        'object': move,
        'page_title': 'Confirmer la suppression',
        'cancel_url': 'stock_move_list',
    })

# Generate global stock moves pdf
def stock_move_pdf(request):
    state = request.GET.get('state', '')
    operation_type = request.GET.get('operation_type', '')
    
    moves = StockMove.objects.select_related('operation_type', 'source_location', 'dest_location', 'department', 'supplier').prefetch_related('lines__product', 'lines__uom').all()
    
    if state:
        moves = moves.filter(state=state)
    
    if operation_type:
        moves = moves.filter(operation_type__label=operation_type)
    
    template = get_template('stock_move_report.html')
    context = {'moves': moves, 'date': timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
    html_string = template.render(context)
    # Generate PDF with WeasyPrint
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="stock_movements_report.pdf"'
    HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(
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
    log_action(request.user, moves, 'impression')
    return response

# Details JSON for export or API
def stock_move_detail_json(request, pk):
    move = get_object_or_404(
        StockMove.objects.select_related(
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
                'product': line.product.name,
                'quantity_demanded': line.quantity_demanded,
                'quantity_arrived': line.quantity_arrived,
                'uom': line.uom.label,
            } for line in move.lines.all()
        ],
    }
    return JsonResponse(data, json_dumps_params={'indent': 2})

# Pdf for every mouvement
@require_GET
def stock_move_delivery_pdf(request, pk):
    move = get_object_or_404(
        StockMove.objects.select_related(
            'source_location', 'dest_location', 'operation_type', 'department', 'supplier', 'created_by'
        ).prefetch_related('lines__product', 'lines__uom'),
        pk=pk, state=StockMove.DONE
    )
    context = {
        'move': move,
        'lines': move.lines.all(),
        'date': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
        'page_title': 'Bon de Livraison',
    }
    html_string = render_to_string('stock_move_delivery_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="delivery_{move.reference}.pdf"'
    HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(response)
    log_action(request.user, move, 'impression')
    return response

# ---------------------------------INVENTORY ------------------------------------------------------------------
def inventory_list(request):
    # Get all categories for the filter
    categories = Category.objects.all().order_by('label')
    
    return render(request, 'inventory.html', {
        'page_title': 'Inventaire des Produits',
        'categories': categories,
        'current_category': request.GET.get('category', ''),
    })

def inventory_list_json(request):
    page_number = request.GET.get('page', 1)
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    sort_by = request.GET.get('sort_by', '-product_id')
    sort_order = request.GET.get('sort_order', 'asc')

    # Mapping frontend sort fields to model fields
    sort_mapping = {
        'default_code': 'default_code',
        'name': 'name',
        'category': 'categ__label',
        'total_quantity': 'total_quantity_cached',
    }
    sort_field = sort_mapping.get(sort_by, '-product_id')

    # Apply sort order
    if sort_order == 'desc':
        sort_field = f'-{sort_field}'

    products = Product.objects.all().order_by(sort_field)
    
    # Filter by category if provided
    if category:
        products = products.filter(categ__label=category)
    
    # Search by multiple fields
    if query:
        normalized_query = query.replace(',', '.')
        
        products = products.filter(
            Q(name__icontains=query) |
            Q(default_code__icontains=query) |
            Q(categ__label__icontains=query) |
            Q(total_quantity_cached__icontains=normalized_query)
        )

    paginator = Paginator(products, 5)
    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(1)

    product_data = []
    for product in page_obj:
        product_locations = list(
            ProductLocation.objects.filter(product=product)
            .values('location', 'quantity_stored', 'location__name')
        )
        for loc in product_locations:
            loc['location_id'] = loc.pop('location')  
            loc['quantity_stored'] = float(loc['quantity_stored'])
            loc['location_name'] = loc.pop('location__name')
        product_data.append({
            'id': product.pk,
            'name': product.name,
            'default_code': product.default_code,
            'category': product.categ.label if product.categ else '',
            'standard_price': product.standard_price,
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

def inventory_pdf(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    products = Product.objects.all().order_by('-product_id')
    
    # Filter by category if provided
    if category:
        products = products.filter(categ__label=category)
    
    # Search by multiple fields
    if query:
        normalized_query = query.replace(',', '.')
        products = products.filter(
            Q(name__icontains=query) |
            Q(default_code__icontains=query) |
            Q(categ__label__icontains=query) |
            Q(total_quantity_cached__icontains=normalized_query)
        )
    
    product_data = []

    for product in products:
        product_locations = list(
            ProductLocation.objects.filter(product=product)
            .values('location', 'quantity_stored', 'location__name')
        )
        for loc in product_locations:
            loc['location_id'] = loc.pop('location')  
            loc['quantity_stored'] = float(loc['quantity_stored'])
            loc['location_name'] = loc.pop('location__name')
        product_data.append({
            'id': product.pk,
            'name': product.name,
            'default_code': product.default_code,
            'category': product.categ.label if product.categ else '',
            'standard_price': product.standard_price,
            'total_quantity': float(product.total_quantity) if product.total_quantity else 0.0,
            'locations': product_locations,
        })

    html_string = render_to_string('inventory_pdf.html', {
        'products': product_data,
        'date': datetime.date.today().strftime('%Y-%m-%d'),
        'page_title': 'Inventaire des Produits',
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="inventory_{datetime.date.today().strftime("%Y%m%d")}.pdf"'
    HTML(string=html_string).write_pdf(response)
    log_action(request.user, products, 'impression')
    return response

# Inventory Adjustment
def inventory_adjustment(request):
    from django.db.models import Q
    if request.method == 'POST':
        updated_count = 0
        with transaction.atomic():
            product_locations = ProductLocation.objects.select_related('product', 'location').all()

            for pl in product_locations:
                input_key = f'counted_{pl.product_location_id}'
                counted_qty = request.POST.get(input_key, '').strip()

                try:
                    if counted_qty != '' and counted_qty is not None:
                        qty = float(counted_qty)
                        if qty < 0:
                            request.session['swal_error'] = f'Quantité négative non autorisée pour {pl.product.name} @ {pl.location.name}.'
                            return redirect('inventory_adjustment')
                        # save only if different from stored quantity
                        if qty != pl.quantity_stored:
                            pl.quantity_counted = qty
                            pl.last_count_date = timezone.now().date()
                            pl.save()
                            log_action(request.user, pl, 'modification')
                            updated_count += 1
                except ValueError:
                    request.session['swal_error'] = f'Valeur invalide pour {pl.product.name} @ {pl.location.name}.'
                    return redirect('inventory_adjustment')

        request.session['swal_success'] = 'Emplacements ajustés avec succès.'
        return redirect('inventory_adjustment')
    swal_success = request.session.pop('swal_success', None)
    swal_error = request.session.pop('swal_error', None)
    
    # Récupérer le paramètre de recherche
    query = request.GET.get('q', '').strip()
    
    # Get sorting parameters
    sort_by = request.GET.get('sort_by', 'product__default_code')
    sort_order = request.GET.get('sort_order', 'asc')

    # Define a mapping from simple names to complex model fields
    sort_mapping = {
        'default_code': 'product__default_code',
        'product': 'product__name',
        'location': 'location__name',
        'quantity_stored': 'quantity_stored',
        'last_count_date': 'last_count_date',
    }

    # Get the actual field name from the mapping, default to 'product__default_code'
    sort_field = sort_mapping.get(sort_by, 'product__default_code')

    # Apply sort order
    if sort_order == 'desc':
        sort_field = f'-{sort_field}'

    # get all locations with their quantity_counted
    locations = ProductLocation.objects.select_related('product', 'location').order_by(sort_field)
    
    # Appliquer le filtre de recherche si fourni
    if query:
        locations = locations.filter(
            Q(product__default_code__icontains=query) |
            Q(product__name__icontains=query) |
            Q(location__name__icontains=query) |
            Q(quantity_stored__icontains=query)
        )
    
    # pagination
    paginator = Paginator(locations, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'inventory_adjustment.html', {
        'page_title': 'Ajustement de l\'inventaire',
        'locations': page_obj.object_list,
        'page_obj': page_obj,
        'swal_success': swal_success,
        'swal_error': swal_error,
        'sort_by': sort_by,
        'sort_order': sort_order,
        'query': query,
    })

# Adjustement pdf
def inventory_adjustment_pdf(request):
    locations = ProductLocation.objects.select_related('product', 'location').order_by('product__default_code')
    adjusted_locations = []
    total_diff_cost = Decimal('0.0')

    for loc in locations:
        quantity_counted = loc.quantity_counted if loc.quantity_counted is not None else Decimal('0.0')
        quantity_stored = loc.quantity_stored if loc.quantity_stored is not None else Decimal('0.0')
        standard_price = Decimal(str(loc.product.standard_price or 0.0))

        # Calculate difference and cost
        loc.diff = quantity_counted - quantity_stored
        loc.diff_value = loc.diff * standard_price
        total_diff_cost += loc.diff_value
        adjusted_locations.append(loc)

    # Render the template with the adjusted data
    html_string = render_to_string('inventory_adjustment_pdf.html', {
        'page_title': "Rapport d'Ajustement d'Inventaire",
        'date': timezone.now().date(),
        'locations': adjusted_locations,
        'total_diff_cost': total_diff_cost,
    })

    # Generate PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="adjustment_{timezone.now().date().strftime("%Y%m%d")}.pdf"'
    HTML(string=html_string).write_pdf(response)
    log_action(request.user, adjusted_locations, 'impression')
    return response

# ------------------------VALUATION ------------------------------------------------------------------
def valuation_list(request):
    # Get all categories for the filter
    categories = Category.objects.all().order_by('label')
    
    return render(request, 'valuation.html', {
        'page_title': 'Valorisation de l\'inventaire',
        'categories': categories,
        'current_category': request.GET.get('category', ''),
    })

def valuation_list_json(request):
    page_number = request.GET.get('page', 1)
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    sort_by = request.GET.get('sort_by', 'name')
    sort_order = request.GET.get('sort_order', 'asc')

    # Annotate queryset with total_price for sorting
    products_qs = Product.objects.annotate(
        total_price=ExpressionWrapper(
            F('standard_price') * F('total_quantity_cached'),
            output_field=DecimalField()
        )
    )

    # Map frontend sort fields to model/annotated fields
    sort_mapping = {
        'default_code': 'default_code',
        'name': 'name',
        'category': 'categ__label',
        'standard_price': 'standard_price',
        'total_quantity': 'total_quantity_cached',
        'total_price': 'total_price',
    }
    sort_field = sort_mapping.get(sort_by, 'name')

    if sort_order == 'desc':
        sort_field = f'-{sort_field}'

    products_qs = products_qs.order_by(sort_field)
    
    # Filter by category if provided
    if category:
        products_qs = products_qs.filter(categ__label=category)
    
    # Search by multiple fields
    if query:
        normalized_query = query.replace(',', '.')
        products_qs = products_qs.filter(
            Q(name__icontains=query) |
            Q(default_code__icontains=query) |
            Q(categ__label__icontains=query) |
            Q(standard_price__icontains=normalized_query) |
            Q(total_quantity_cached__icontains=normalized_query)
        )

    # Recalculate total stock value on the filtered queryset
    total_stock_value = products_qs.aggregate(total_value=Sum('total_price'))['total_value'] or Decimal('0')

    paginator = Paginator(products_qs, 5)
    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(1)

    product_data = []
    for product in page_obj:
        product_locations = list(
            ProductLocation.objects.filter(product=product)
            .values('location', 'quantity_stored', 'location__name')
        )
        for loc in product_locations:
            loc['location_id'] = loc.pop('location')  
            quantity_stored = Decimal(str(loc['quantity_stored'] or 0))
            loc['quantity_stored'] = float(quantity_stored)
            loc['location_name'] = loc.pop('location__name')
            location_price = (product.standard_price or Decimal('0')) * quantity_stored
            loc['location_price'] = float(location_price)

        total_quantity = Decimal(str(product.total_quantity or 0))
        # The total_price is now annotated on the product object
        total_price = product.total_price if hasattr(product, 'total_price') else Decimal('0')

        product_data.append({
            'id': product.pk,
            'name': product.name,
            'default_code': product.default_code,
            'category': product.categ.label if product.categ else '',
            'standard_price': float(product.standard_price or 0),
            'total_quantity': float(total_quantity),
            'total_price': float(total_price),
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
        'total_stock_value': float(total_stock_value),
    })

def valuation_pdf(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    products = Product.objects.all().order_by('-product_id')
    
    # Filter by category if provided
    if category:
        products = products.filter(categ__label=category)
    
    # Search by multiple fields
    if query:
        normalized_query = query.replace(',', '.')
        products = products.filter(
            Q(name__icontains=query) |
            Q(default_code__icontains=query) |
            Q(categ__label__icontains=query) |
            Q(standard_price__icontains=normalized_query) |
            Q(total_quantity_cached__icontains=normalized_query)
        )

    # Corriger le calcul de total_stock_value
    total_stock_value = sum(
        (product.standard_price or Decimal('0')) * Decimal(str(product.total_quantity or 0))
        for product in products
    )

    product_data = []
    for product in products:
        product_locations = list(
            ProductLocation.objects.filter(product=product)
            .values('location', 'quantity_stored', 'location__name')
        )
        for loc in product_locations:
            loc['location_id'] = loc.pop('location')  #
            quantity_stored = Decimal(str(loc['quantity_stored'] or 0))
            loc['quantity_stored'] = float(quantity_stored)
            loc['location_name'] = loc.pop('location__name')
            location_price = (product.standard_price or Decimal('0')) * quantity_stored
            loc['location_price'] = float(location_price)

        total_quantity = Decimal(str(product.total_quantity or 0))
        total_price = (product.standard_price or Decimal('0')) * total_quantity

        product_data.append({
            'id': product.pk,
            'name': product.name,
            'default_code': product.default_code,
            'category': product.categ.label if product.categ else '',
            'standard_price': float(product.standard_price or 0),
            'total_quantity': float(total_quantity),
            'total_price': float(total_price),
            'locations': product_locations,
        })

    html_string = render_to_string('valuation_pdf.html', {
        'products': product_data,
        'date': datetime.date.today().strftime('%Y-%m-%d'),
        'page_title': 'Valorisation de l\'Inventaire',
        'total_stock_value': float(total_stock_value),
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="valuation_{datetime.date.today().strftime("%Y%m%d")}.pdf"'
    HTML(string=html_string).write_pdf(response)
    log_action(request.user, products, 'impression')
    return response

# ------------------------EXPORT product pdf------------------------------------------------------------------
def product_export(request):
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    selected_ids = request.GET.get('ids', '')  
    select_all = request.GET.get('select_all', '') 
    # Get sorting parameters for consistent ordering
    sort_by = request.GET.get('sort_by', 'product_id')
    sort_order = request.GET.get('sort_order', 'desc')
    # Mapping des colonnes pour le tri
    sort_mapping = {
        'default_code': 'default_code',
        'name': 'name',
        'category': 'categ__label',
        'standard_price': 'standard_price',
        'stock_minimal': 'stock_minimal',
        'uom': 'uom__symbole',
        'total_quantity': 'total_quantity_cached',
        'product_id': 'product_id'
    }
    # Validate sort_by column
    sort_field = sort_mapping.get(sort_by, 'product_id')
    order_prefix = '-' if sort_order == 'desc' else ''
    
    products = Product.objects.all().order_by(f'{order_prefix}{sort_field}')
    initial_count = products.count()
    # If "select all" is activated, export all filtered items
    if select_all == 'true':
        # Apply search and category filters
        if query:
            normalized_query = query.replace(',', '.')
            products = products.filter(
                Q(name__icontains=query) |
                Q(default_code__icontains=query) |
                Q(categ__label__icontains=query) |
                Q(standard_price__icontains=normalized_query) |
                Q(stock_minimal__icontains=query) |
                Q(uom__symbole__icontains=query) |  
                Q(uom__label__icontains=query) |    
                Q(total_quantity_cached__icontains=normalized_query)
            )
        if category_filter:
            products = products.filter(categ__label=category_filter)
        return generate_export_pdf(products, query, category_filter)
    # If specific IDs are selected, filter only those products
    elif selected_ids:
        try:
            ids_list = [int(id.strip()) for id in selected_ids.split(',') if id.strip().isdigit()]
            if ids_list:
                products = products.filter(product_id__in=ids_list)
                return generate_export_pdf(products, query, category_filter)
        except (ValueError, AttributeError) as e:
            # In case of error in ID parsing, continue with all products
            pass
    # Search by all fields (only if no specific IDs are selected)
    if query and not selected_ids:
        products = products.filter(
            Q(default_code__icontains=query) |
            Q(name__icontains=query) |
            Q(categ__label__icontains=query) |
            Q(standard_price__icontains=query) |
            Q(total_quantity_cached__icontains=query) |
            Q(barcode__icontains=query) |
            Q(dci__label__icontains=query) |
            Q(uom__symbol__icontains=query) 
        )
    # Filter by category (only if no specific IDs are selected)
    if category_filter and not selected_ids:
        products = products.filter(categ__label=category_filter)
    # Generate the PDF with the helper function
    return generate_export_pdf(products, query, category_filter)

def generate_export_pdf(products, query='', category_filter=''):
    html_string = render_to_string('product_export_pdf.html', {
        'products': products,
        'query': query,
        'category_filter': category_filter,
        'export_date': timezone.now(),
    })
    pdf = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="produits_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    if products.exists():
        log_action(request.user, products.first(), 'impression')
    return response

def inventory_statistics(request):
    """Vue pour afficher les statistiques de l'inventaire"""
    
    # Statistiques principales
    total_products = Product.objects.filter(active=True).count()
    total_stock_moves = StockMove.objects.count()
    total_categories = Category.objects.count()
    low_stock_products = Product.objects.filter(
        active=True,
        total_quantity_cached__lte=F('stock_minimal')
    ).count()
    
    # Mouvements par statut
    moves_by_status = StockMove.objects.values('state').annotate(
        count=Count('move_id')
    )
    
    # Produits par catégorie
    products_by_category = Category.objects.annotate(
        product_count=Count('product', filter=Q(product__active=True))
    ).filter(product_count__gt=0).order_by('-product_count')[:10]
    
    # Valeur totale du stock
    total_stock_value = Product.objects.filter(active=True).aggregate(
        total_value=Sum(F('total_quantity_cached') * F('standard_price'))
    )['total_value'] or 0
    
    # Mouvements par mois (6 derniers mois)
    moves_by_month = []
    for i in range(6):
        month_start = (timezone.now().replace(day=1) - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        count = StockMove.objects.filter(
            date_created__gte=month_start,
            date_created__lte=month_end
        ).count()
        
        moves_by_month.append({
            'month_name': month_start.strftime('%B %Y'),
            'count': count
        })
    
    moves_by_month.reverse()
    
    # Produits récents (5 derniers)
    recent_products = Product.objects.filter(active=True).order_by('-product_id')[:5]
    
    # Mouvements récents (5 derniers)
    recent_moves = StockMove.objects.select_related(
        'operation_type', 'source_location', 'dest_location'
    ).order_by('-date_created')[:5]
    
    # Produits en rupture de stock
    out_of_stock = Product.objects.filter(
        active=True,
        total_quantity_cached=0
    ).count()
    
    # Produits par type - vérifier s'il y a des données
    try:
        products_by_type = ProductType.objects.annotate(
            product_count=Count('product', filter=Q(product__active=True))
        ).filter(product_count__gt=0).order_by('-product_count')[:10]
    except:
        products_by_type = []
    
    # Préparer les données JSON pour les graphiques
    moves_status_json = json.dumps([
        {'status': item['state'], 'count': item['count']} 
        for item in moves_by_status
    ])
    
    products_category_json = json.dumps([
        {'category': category.label, 'count': category.product_count} 
        for category in products_by_category
    ])
    
    moves_month_json = json.dumps([
        {'month_name': month['month_name'], 'count': month['count']} 
        for month in moves_by_month
    ])
    
    products_type_json = json.dumps([
        {'type': ptype.label, 'count': ptype.product_count} 
        for ptype in products_by_type
    ] if products_by_type else [])
    
    stock_status_json = json.dumps([
        {'status': 'Stock normal', 'count': total_products - low_stock_products - out_of_stock},
        {'status': 'Stock faible', 'count': low_stock_products},
        {'status': 'Rupture', 'count': out_of_stock}
    ])
    
    context = {
        'total_products': total_products,
        'total_stock_moves': total_stock_moves,
        'total_categories': total_categories,
        'low_stock_products': low_stock_products,
        'out_of_stock': out_of_stock,
        'total_stock_value': total_stock_value,
        'moves_by_status': moves_by_status,
        'products_by_category': products_by_category,
        'products_by_type': products_by_type,
        'moves_by_month': moves_by_month,
        'recent_products': recent_products,
        'recent_moves': recent_moves,
        'moves_status_json': moves_status_json,
        'products_category_json': products_category_json,
        'moves_month_json': moves_month_json,
        'products_type_json': products_type_json,
        'stock_status_json': stock_status_json,
    }
    
    return render(request, 'inventory_statistics.html', context)