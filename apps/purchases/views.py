from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.template.loader import render_to_string
from django.conf import settings
try:
    from weasyprint import HTML
except Exception:
    HTML = None
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib import messages
from django.forms import modelformset_factory
from django.utils import timezone
from decimal import Decimal
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncMonth
from django.db.models import Q
from django.contrib.auth import get_user_model
import json
from decimal import Decimal, InvalidOperation  # Importer InvalidOperation

import re
from apps.inventory.models import Product, ProductLocation, StockLocation, Category, UnitOfMesure, ProductType, StockMove, LineStockMove, OperationType
from .models import Supplier, Country, City, Language, Tax, PurchaseOrder, PurchaseOrderLine, Currency, PaymentMode, ConventionType, Convention, ConventionLine
from .forms import SupplierForm, CountryForm, CityForm, LanguageForm, TaxForm, PurchaseOrderForm, PurchaseOrderLineForm, ConventionTypeForm, ConventionForm, ConventionLineForm, PaymentModeForm
from apps.inventory.forms import ProductForm
from apps.home.utils import log_action
from django.urls import reverse
from django.db import models  # Add this import to resolve the NameError
def supplier_list(request):
    """
    Displays a list of all suppliers and handles creation/update of supplier records.
    """
    suppliers = Supplier.objects.all()
    countries = Country.objects.all()
    cities = City.objects.all()
    languages = Language.objects.all()
    supplier_id = request.POST.get('supplier_id') or request.GET.get('edit')
    supplier = get_object_or_404(Supplier, pk=supplier_id) if supplier_id else None

    if request.method == 'POST':
        data = request.POST
        files = request.FILES
        try:
            if supplier:
                supplier.name = data.get('name')
                supplier.is_company = (data.get('is_company') == 'True')
                supplier.street = data.get('street')
                supplier.street2 = data.get('street2')
                supplier.zip = data.get('zip')
                supplier.city = City.objects.get(pk=data.get('city')) if data.get('city') else None
                supplier.country = Country.objects.get(pk=data.get('country')) if data.get('country') else None
                supplier.email = data.get('email')
                supplier.phone = data.get('phone')
                supplier.mobile = data.get('mobile')
                supplier.ICE = data.get('ICE')
                supplier.RC = data.get('RC') or None
                supplier.IF = data.get('IF') or None
                supplier.lang = Language.objects.get(pk=data.get('lang')) if data.get('lang') else None
                supplier.vat = data.get('vat')
                supplier.RIB = data.get('RIB')
                supplier.comment = data.get('comment')
                if 'logo' in files and files.get('logo'):
                    supplier.logo = files.get('logo')
                supplier.save()
                log_action(request.user, supplier, 'modification')
                status = 'updated'
            else:
                supplier = Supplier.objects.create(
                    name=data.get('name'),
                    is_company=(data.get('is_company') == 'True'),
                    street=data.get('street'),
                    street2=data.get('street2'),
                    zip=data.get('zip'),
                    city=City.objects.get(pk=data.get('city')) if data.get('city') else None,
                    country=Country.objects.get(pk=data.get('country')) if data.get('country') else None,
                    email=data.get('email'),
                    phone=data.get('phone'),
                    mobile=data.get('mobile'),
                    ICE=data.get('ICE'),
                    RC=data.get('RC') or None,
                    IF=data.get('IF') or None,
                    lang=Language.objects.get(pk=data.get('lang')) if data.get('lang') else None,
                    vat=data.get('vat'),
                    RIB=data.get('RIB'),
                    comment=data.get('comment'),
                    logo=files.get('logo')
                )
                log_action(request.user, supplier, 'creation')
                status = 'created'
            return redirect(f"{reverse('supplier_list')}?status={status}")
        except Exception as e:
            print(f"Erreur lors de la création/modification du fournisseur : {e}")
            return redirect(f"{reverse('supplier_list')}?status=error")
    return render(request, 'purchases.html', {
        'suppliers': suppliers,
        'countries': countries,
        'cities': cities,
        'languages': languages,
        'supplier': supplier,
    })

@csrf_exempt
def supplier_list_filtered(request):
    if request.method == 'POST':
        search = request.POST.get('search', '')
        country = request.POST.get('country', '')
        city = request.POST.get('city', '')
        suppliers = Supplier.objects.all()
        if search:
            suppliers = suppliers.filter(name__icontains=search) | suppliers.filter(email__icontains=search)
        if country:
            suppliers = suppliers.filter(country__name=country)
        if city:
            suppliers = suppliers.filter(city__name=city)
        supplier_data = [
            {
                'pk': supplier.pk,
                'name': supplier.name,
                'email': supplier.email,
                'phone': supplier.phone,
                'street': supplier.street,
                'street2': supplier.street2,
                'country': {'name': supplier.country.name} if supplier.country else None,
                'city': {'name': supplier.city.name} if supplier.city else None
            }
            for supplier in suppliers
        ]
        return JsonResponse({'suppliers': supplier_data})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def supplier_delete(request, pk):
    if request.method == 'POST':
        supplier = get_object_or_404(Supplier, pk=pk)
        supplier.delete()
        log_action(request.user, supplier, 'suppression')
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

@require_http_methods(["GET"])
def supplier_order_history(request, pk):
    try:
        supplier = get_object_or_404(Supplier, pk=pk)
        # Filtrer uniquement les commandes confirmées (state='confirmed')
        orders = PurchaseOrder.objects.filter(partner=supplier, state='confirmed').select_related('currency')
        total_orders = orders.count()
        turnover = orders.aggregate(total=Sum('amount_total'))['total'] or 0.0
        turnover = float(turnover)
        orders_by_state = orders.values('state').annotate(count=Count('id')).order_by('state')
        state_labels = [dict(PurchaseOrder.STATE_CHOICES).get(entry['state'], entry['state']) for entry in orders_by_state]
        state_data = [entry['count'] for entry in orders_by_state]
        order_details = [{
            'id': order.id,
            'name': order.name,
            'date_order': order.date_order.strftime('%Y-%m-%d') if order.date_order else 'N/A',
            'amount_total': float(order.amount_total) if order.amount_total else 0,
            'state': order.get_state_display(),
            'currency': 'MAD'
        } for order in orders]
        return JsonResponse({
            'success': True,
            'supplier_name': supplier.name,
            'total_orders': total_orders,
            'turnover': turnover,
            'chart_data': {'labels': state_labels, 'data': state_data},
            'orders': order_details
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_http_methods(["GET"])
def supplier_order_history_pdf(request, pk):
    try:
        supplier = get_object_or_404(Supplier, pk=pk)
        # Filtrer uniquement les commandes confirmées (state='confirmed')
        orders = PurchaseOrder.objects.filter(partner=supplier, state='confirmed').select_related('currency')
        total_orders = orders.count()
        turnover = orders.aggregate(total=Sum('amount_total'))['total'] or 0.0
        turnover = float(turnover)
        orders_by_state = orders.values('state').annotate(count=Count('id')).order_by('state')
        state_data = [
            {'state': dict(PurchaseOrder.STATE_CHOICES).get(entry['state'], entry['state']), 'count': entry['count']}
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
        html_string = render_to_string('supplier_order_history_pdf.html', context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="order_history_{supplier.name.replace(" ", "_")}.pdf"'
        HTML(string=html_string).write_pdf(response)
        log_action(request.user, supplier, 'impression')
        return response
    except Exception as e:
        return HttpResponse(f"Erreur lors de la génération du PDF : {str(e)}", status=500)

def country_list(request):
    countries = list(Country.objects.values('id', 'name'))
    return JsonResponse({'countries': countries})

@csrf_exempt
def country_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            if name:
                name = name.strip()
                if Country.objects.filter(name__iexact=name).exists():
                    return JsonResponse({'success': False, 'error': 'Le pays existe déjà.'})
                country = Country.objects.create(name=name)
                log_action(request.user, country, 'creation')
                return JsonResponse({'success': True, 'id': country.id, 'name': country.name})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

@csrf_exempt
def country_delete(request, pk):
    if request.method == 'POST':
        country = get_object_or_404(Country, pk=pk)
        country.delete()
        log_action(request.user, country, 'suppression')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

def city_list(request):
    cities = list(City.objects.select_related('country').values('id', 'name', 'country__name'))
    return JsonResponse({'cities': cities})

@csrf_exempt
def city_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            country_id = data.get('country')
            if name and country_id:
                country = get_object_or_404(Country, id=country_id)
                if City.objects.filter(name__iexact=name.strip(), country=country).exists():
                    return JsonResponse({'success': False, 'error': 'La ville existe déjà.'})
                city = City.objects.create(name=name.strip(), country=country)
                log_action(request.user, city, 'creation')
                return JsonResponse({
                    'success': True,
                    'id': city.id,
                    'name': city.name,
                    'country_name': city.country.name
                })
        except Country.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Pays non trouvé'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Données invalides'})

@csrf_exempt
def city_delete(request, pk):
    if request.method == 'POST':
        city = get_object_or_404(City, pk=pk)
        city.delete()
        log_action(request.user, city, 'suppression')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

def language_list(request):
    languages = list(Language.objects.values('id', 'name'))
    return JsonResponse({'languages': languages})

@csrf_exempt
def language_create(request):
    if request.method == 'POST':
        try:
            data = request.POST if request.headers.get('Content-Type') != 'application/json' else json.loads(request.body)
            name = data.get('name')
            if name:
                name = name.strip()
                if Language.objects.filter(name__iexact=name).exists():
                    return JsonResponse({'success': False, 'error': 'La langue existe déjà.'})
                language = Language.objects.create(name=name)
                log_action(request.user, language, 'creation')
                return JsonResponse({'success': True, 'id': language.id, 'name': language.name})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

@csrf_exempt
def language_delete(request, pk):
    if request.method == 'POST':
        language = get_object_or_404(Language, pk=pk)
        language.delete()
        log_action(request.user, language, 'suppression')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

def tax_list(request):
    taxes = list(Tax.objects.values('id', 'libelle', 'valeur'))
    return JsonResponse({'taxes': taxes})

@csrf_exempt
def tax_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            libelle = data.get('libelle')
            valeur = data.get('valeur')
            if libelle and valeur is not None:
                libelle = libelle.strip()
                if Tax.objects.filter(libelle__iexact=libelle).exists():
                    return JsonResponse({'success': False, 'error': 'Cette taxe existe déjà.'})
                tax = Tax.objects.create(libelle=libelle, valeur=valeur)
                log_action(request.user, tax, 'creation')
                return JsonResponse({'success': True, 'id': tax.id, 'libelle': tax.libelle, 'valeur': str(tax.valeur)})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Données invalides'})

@csrf_exempt
def tax_delete(request, pk):
    if request.method == 'POST':
        tax = get_object_or_404(Tax, pk=pk)
        tax.delete()
        log_action(request.user, tax, 'suppression')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

def list_currencies(request):
    currencies = list(Currency.objects.values('id', 'libelle', 'abreviation'))
    return JsonResponse({'currencies': currencies})

@csrf_exempt
def create_currency(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            libelle = data.get('libelle')
            abreviation = data.get('abreviation')
            if not libelle or not abreviation:
                return JsonResponse({'success': False, 'error': 'Libellé et abréviation requis'})
            currency = Currency.objects.create(libelle=libelle, abreviation=abreviation)
            log_action(request.user, currency, 'creation')
            return JsonResponse({
                'success': True,
                'id': currency.id,
                'libelle': currency.libelle,
                'abreviation': currency.abreviation
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

@csrf_exempt
def delete_currency(request, pk):
    if request.method == 'POST':
        currency = get_object_or_404(Currency, pk=pk)
        try:
            currency.delete()
            log_action(request.user, currency, 'suppression')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})



def purchases_configuration(request):
    # Fetch querysets
    countries = Country.objects.all()
    cities = City.objects.select_related('country').all()
    languages = Language.objects.all()
    taxes = Tax.objects.all()
    currencies = Currency.objects.all()
    payment_modes = PaymentMode.objects.all()
    convention_types = ConventionType.objects.all()

    # Apply search filters
    search_country = request.GET.get('search_country', '')
    search_city = request.GET.get('search_city', '')
    search_language = request.GET.get('search_language', '')
    search_tax = request.GET.get('search_tax', '')
    search_currency = request.GET.get('search_currency', '')
    search_payment_mode = request.GET.get('search_payment_mode', '')
    search_convention_type = request.GET.get('search_convention_type', '')

    if search_country:
        countries = countries.filter(name__icontains=search_country)
    if search_city:
        cities = cities.filter(name__icontains=search_city) | cities.filter(country__name__icontains=search_city)
    if search_language:
        languages = languages.filter(name__icontains=search_language)
    if search_tax:
        taxes = taxes.filter(libelle__icontains=search_tax)
    if search_currency:
        currencies = currencies.filter(libelle__icontains=search_currency) | currencies.filter(abreviation__icontains=search_currency)
    if search_payment_mode:
        payment_modes = payment_modes.filter(name__icontains=search_payment_mode)
    if search_convention_type:
        convention_types = convention_types.filter(libelle__icontains=search_convention_type)

    # Paginate querysets (5 items per page)
    paginator_countries = Paginator(countries, 5)
    paginator_cities = Paginator(cities, 5)
    paginator_languages = Paginator(languages, 5)
    paginator_taxes = Paginator(taxes, 5)
    paginator_currencies = Paginator(currencies, 5)
    paginator_payment_modes = Paginator(payment_modes, 5)
    paginator_convention_types = Paginator(convention_types, 5)

    # Get page numbers from query parameters
    page_country = request.GET.get('page_country', 1)
    page_city = request.GET.get('page_city', 1)
    page_language = request.GET.get('page_language', 1)
    page_tax = request.GET.get('page_tax', 1)
    page_currency = request.GET.get('page_currency', 1)
    page_payment_mode = request.GET.get('page_payment_mode', 1)
    page_convention_type = request.GET.get('page_convention_type', 1)

    # Get paginated objects
    countries = paginator_countries.get_page(page_country)
    cities = paginator_cities.get_page(page_city)
    languages = paginator_languages.get_page(page_language)
    taxes = paginator_taxes.get_page(page_tax)
    currencies = paginator_currencies.get_page(page_currency)
    payment_modes = paginator_payment_modes.get_page(page_payment_mode)
    convention_types = paginator_convention_types.get_page(page_convention_type)

    # Initialize forms
    payment_form = PaymentModeForm()
    convention_form = ConventionTypeForm()

    # Handle POST request for convention type
    if request.method == 'POST' and 'libelle' in request.POST:
        convention_form = ConventionTypeForm(request.POST)
        if convention_form.is_valid():
            convention_form.save()
            log_action(request.user, convention_form.instance, 'creation')
            return redirect(request.path_info + '?success=1')

    # Render template with context
    return render(request, 'configuration.html', {
        'countries': countries,
        'cities': cities,
        'languages': languages,
        'taxes': taxes,
        'currencies': currencies,
        'payment_modes': payment_modes,
        'payment_form': payment_form,
        'convention_types': convention_types,
        'convention_form': convention_form,
    })

def purchase_order_list(request):
    orders = PurchaseOrder.objects.all().select_related('partner')
    suppliers = Supplier.objects.all()
    products = Product.objects.all()
    currencies = Currency.objects.all()
    taxes = Tax.objects.all()
    payment_modes = PaymentMode.objects.all()
    context = {
        'orders': orders,
        'suppliers': suppliers,
        'products': products,
        'currencies': currencies,
        'taxes': taxes,
        'payment_modes': payment_modes,
        'page_title': 'Commandes'
    }
    return render(request, 'orders.html', context)

@transaction.atomic
def create_purchase_order(request):
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier')
        date_order = request.POST.get('order_date')
        currency_id = request.POST.get('currency')
        payment_mode_id = request.POST.get('payment_mode')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        # Validate required fields
        if not all([supplier_id, date_order, currency_id]):
            error_message = 'Veuillez remplir tous les champs obligatoires.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_message}, status=400)
            messages.error(request, error_message)
            return render(request, 'new_order.html', {
                'products': Product.objects.all(),
                'suppliers': Supplier.objects.all(),
                'currencies': Currency.objects.all(),
                'taxes': Tax.objects.all(),
                'payment_modes': PaymentMode.objects.all(),
                'page_title': 'Nouvelle Commande',
            })

        # Generate reference
        last_order = PurchaseOrder.objects.order_by('-id').first()
        next_id = (last_order.id + 1) if last_order else 1
        reference = f'PR-{next_id:06d}'

        # Fetch related objects
        try:
            supplier = get_object_or_404(Supplier, pk=supplier_id)
            currency = get_object_or_404(Currency, pk=currency_id)
            payment_mode = get_object_or_404(PaymentMode, pk=payment_mode_id) if payment_mode_id else None
        except Exception as e:
            error_message = f'Erreur lors de la récupération des données : {str(e)}'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_message}, status=400)
            messages.error(request, error_message)
            return render(request, 'new_order.html', {
                'products': Product.objects.all(),
                'suppliers': Supplier.objects.all(),
                'currencies': Currency.objects.all(),
                'taxes': Tax.objects.all(),
                'payment_modes': PaymentMode.objects.all(),
                'page_title': 'Nouvelle Commande',
                'reference': reference,
            })

        # Create order
        order = PurchaseOrder.objects.create(
            name=reference,
            partner=supplier,
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
        log_action(request.user, order, 'creation')

        # Process order lines
        products = request.POST.getlist('product[]')
        quantities = request.POST.getlist('quantity[]')
        unit_prices = request.POST.getlist('unit_price[]')
        taxes = request.POST.getlist('tax[]')

        if not products or not quantities or not unit_prices:
            order.delete()
            error_message = 'Au moins une ligne de commande est requise.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_message}, status=400)
            messages.error(request, error_message)
            return render(request, 'new_order.html', {
                'products': Product.objects.all(),
                'suppliers': Supplier.objects.all(),
                'currencies': Currency.objects.all(),
                'taxes': Tax.objects.all(),
                'payment_modes': PaymentMode.objects.all(),
                'page_title': 'Nouvelle Commande',
                'reference': reference,
            })

        for i in range(len(products)):
            product_id = products[i]
            product = Product.objects.filter(pk=product_id).first()
            if product:
                try:
                    qty = Decimal(quantities[i])
                    price_unit = Decimal(unit_prices[i])
                    subtotal = qty * price_unit
                    tax_id = taxes[i] if i < len(taxes) and taxes[i] else None
                    tax = Tax.objects.get(pk=tax_id) if tax_id else None
                    line = PurchaseOrderLine.objects.create(
                        order=order,
                        product=product,
                        product_qty=float(qty),
                        price_unit=price_unit,
                        price_subtotal=subtotal,
                        product_uom=product.uom,
                        tax=tax,
                        name=product.name,
                    )
                    log_action(request.user, line, 'creation')
                    tax_amount = Decimal('0.00')
                    if tax and hasattr(tax, 'valeur'):
                        tax_amount = subtotal * (Decimal(str(tax.valeur)) / Decimal('100.0'))
                    order.amount_untaxed += subtotal
                    order.amount_tax += tax_amount
                except (ValueError, Tax.DoesNotExist) as e:
                    print(f"Error processing line {i}: {e}")
                    continue

        order.amount_total = order.amount_untaxed + order.amount_tax
        order.save()
        log_action(request.user, order, 'modification')

        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': 'Commande créée avec succès.',
                'order_id': order.id,
                'redirect_url': '/purchases/orders/'
            })
        messages.success(request, 'Commande créée avec succès.')
        return redirect('order_list')

    else:
        last_order = PurchaseOrder.objects.order_by('-id').first()
        next_id = (last_order.id + 1) if last_order else 1
        reference = f'PR-{next_id:06d}'
        return render(request, 'new_order.html', {
            'products': Product.objects.all(),
            'suppliers': Supplier.objects.all(),
            'currencies': Currency.objects.all(),
            'taxes': Tax.objects.all(),
            'payment_modes': PaymentMode.objects.all(),
            'page_title': 'Nouvelle Commande',
            'reference': reference,
        })

@csrf_exempt
def delete_purchase_order(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    try:
        order_lines = PurchaseOrderLine.objects.filter(order=order)
        for line in order_lines:
            log_action(request.user, line, 'suppression')
        order.delete()
        log_action(request.user, order, 'suppression')

        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': 'Commande supprimée avec succès.'
            })
        messages.success(request, 'Commande supprimée avec succès.')
        return redirect('order_list')
    except Exception as e:
        error_message = f'Erreur lors de la suppression de la commande : {str(e)}'
        if is_ajax:
            return JsonResponse({'success': False, 'error': error_message}, status=400)
        messages.error(request, error_message)
        return redirect('order_list')

def order_detail_json(request, order_id):
    order = get_object_or_404(PurchaseOrder, pk=order_id)
    supplier = get_object_or_404(Supplier, pk=order.partner.id)
    order_lines = order.order_lines.all()
    order_data = {
        'name': order.name,
        'partner': order.partner.name,
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
        'currency_amount': order.currency.abreviation,
    }
    if order.state == 'delivered':
        order_data['date_delivered'] = order.date_delivered.strftime('%Y-%m-%d') if order.date_delivered else 'Non spécifiée'
        order_data['delivery_status'] = order.delivery_status or 'Non spécifié'
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
        'address': supplier.street + ',' + (supplier.street2 + ',' if supplier.street2 else '') + (supplier.city.name if supplier.city else ''),
        'city': supplier.city.name if supplier.city else '',
    }
    return JsonResponse({
        'order': order_data,
        'order_lines': lines_data,
        'supplier': supplier_data,
    })

def generate_order_c(request, order_id):
    order = get_object_or_404(PurchaseOrder, pk=order_id)
    json_data = order_detail_json(request, order_id).content
    context = json.loads(json_data)
    html_string = render_to_string('order_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="commande_{context["order"]["name"]}.pdf"'
    HTML(string=html_string).write_pdf(response)
    log_action(request.user, order, 'impression')
    return response

def generate_price_request_pdf(request, order_id):
    order = get_object_or_404(PurchaseOrder, pk=order_id)
    json_data = order_detail_json(request, order_id).content
    context = json.loads(json_data)
    html_string = render_to_string('request_price_order.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="demande_prix_{context["order"]["name"]}.pdf"'
    HTML(string=html_string).write_pdf(response)
    log_action(request.user, order, 'impression')
    return response

@require_http_methods(["POST"])
def order_list_filtered(request):
    try:
        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')
        supplier = request.POST.get('supplier', '')
        status = request.POST.get('status', '')
        orders = PurchaseOrder.objects.all().select_related('partner')
        if start_date:
            orders = orders.filter(date_order__gte=start_date)
        if end_date:
            orders = orders.filter(date_order__lte=end_date)
        if supplier:
            orders = orders.filter(partner_id=supplier)
        if status:
            orders = orders.filter(state=status)
        orders_data = [
            {
                'id': order.id,
                'name': order.name,
                'partner_name': order.partner.name if order.partner else '',
                'date_order': order.date_order.strftime('%Y-%m-%d') if order.date_order else '',
                'amount_total': float(order.amount_total) if order.amount_total else 0,
                'state': order.state,
                'state_display': order.get_state_display(),
                'payment_mode': order.payment_mode.name if order.payment_mode else '',
            }
            for order in orders
        ]
        return JsonResponse({'orders': orders_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def order_list(request):
    suppliers = Supplier.objects.all()
    purchase_order_states = PurchaseOrder.STATE_CHOICES
    orders = PurchaseOrder.objects.all()
    return render(request, 'order_list.html', {
        'orders': orders,
        'suppliers': suppliers,
        'purchase_order_states': purchase_order_states,
    })

@csrf_exempt
def edit_order(request, order_id):
    order = get_object_or_404(PurchaseOrder, id=order_id)
    PurchaseOrderLineFormSet = modelformset_factory(
        PurchaseOrderLine,
        form=PurchaseOrderLineForm,
        extra=0,
        can_delete=True
    )
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=order)
        formset = PurchaseOrderLineFormSet(request.POST, prefix='lines', queryset=order.order_lines.all())
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                order = form.save()
                log_action(request.user, order, 'modification')
                
                for form in formset:
                    if form.cleaned_data:
                        if form.cleaned_data.get('DELETE'):
                            if form.instance.pk:
                                log_action(request.user, form.instance, 'suppression')
                                form.instance.delete()
                            continue
                        product = form.cleaned_data.get('product')
                        if not product:
                            continue
                        line = form.save(commit=False)
                        line.order = order
                        qty = line.product_qty or 0
                        price = line.price_unit or 0
                        line.price_subtotal = Decimal(str(qty)) * Decimal(str(price))
                        if not line.product_uom:
                            default_uom = UnitOfMesure.objects.first()
                            if default_uom:
                                line.product_uom = default_uom
                            else:
                                raise ValueError("Aucune unité de mesure disponible")
                        if not line.name:
                            line.name = str(product)
                        line.save()
                        log_action(request.user, line, 'modification' if form.instance.pk else 'creation')
                
                # Recalculate totals
                order.amount_untaxed = Decimal('0.00')
                order.amount_tax = Decimal('0.00')
                for line in order.order_lines.all():
                    subtotal = Decimal(str(line.product_qty)) * line.price_unit
                    tax_amount = Decimal('0.00')
                    if line.tax and hasattr(line.tax, 'valeur'):
                        tax_amount = subtotal * (Decimal(str(line.tax.valeur)) / Decimal('100.0'))
                    order.amount_untaxed += subtotal
                    order.amount_tax += tax_amount
                order.amount_total = order.amount_untaxed + order.amount_tax
                order.save()

                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Commande modifiée avec succès.',
                        'redirect_url': '/purchases/orders/'
                    })
                messages.success(request, 'Commande modifiée avec succès.')
                return redirect('order_list')
        else:
            error_messages = []
            if form.errors:
                error_messages.append("Erreurs dans le formulaire principal : " + ", ".join([f"{field}: {err}" for field, errors in form.errors.items() for err in errors]))
            if formset.non_form_errors():
                error_messages.append("Erreurs générales : " + ", ".join(formset.non_form_errors()))
            if formset.errors:
                for i, form_errors in enumerate(formset.errors):
                    if form_errors:
                        error_messages.append(f"Ligne {i+1} : " + ", ".join([f"{field}: {err}" for field, errors in form_errors.items() for err in errors]))
            error_message = "Veuillez corriger les erreurs suivantes : " + "; ".join(error_messages) if error_messages else "Erreur dans le formulaire. Vérifiez les données saisies."
            
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_message}, status=400)
            messages.error(request, error_message)
    else:
        form = PurchaseOrderForm(instance=order)
        formset = PurchaseOrderLineFormSet(queryset=order.order_lines.all(), prefix='lines')

    context = {
        'form': form,
        'formset': formset,
        'order': order,
        'page_title': f'Modifier la commande {order.name}',
        'suppliers': Supplier.objects.all(),
        'currencies': Currency.objects.all(),
        'products': Product.objects.all(),
        'units': UnitOfMesure.objects.all(),
        'taxes': Tax.objects.all(),
    }
    return render(request, 'edit_order.html', context)

def recalculate_totals(request, order):
    total_untaxed = Decimal('0')
    total_tax = Decimal('0')
    for line in order.order_lines.all():
        if line.price_subtotal:
            total_untaxed += line.price_subtotal
        line_tax_amount = Decimal('0')
        if line.tax and hasattr(line.tax, 'valeur'):
            tax_amount = (line.price_subtotal * Decimal(str(line.tax.valeur))) / Decimal('100')
            line_tax_amount += tax_amount
        total_tax += line_tax_amount
    order.amount_untaxed = total_untaxed
    order.amount_tax = total_tax
    order.amount_total = total_untaxed + total_tax
    order.save()
    log_action(request.user, order, 'modification')  # Log PurchaseOrder update

@require_http_methods(["POST"])
@csrf_exempt
def delete_order_line(request, line_id):
    try:
        line = get_object_or_404(PurchaseOrderLine, id=line_id)
        order = line.order
        log_action(request.user, line, 'suppression')  # Log PurchaseOrderLine deletion
        line.delete()
        recalculate_totals(request, order)  # Pass request to recalculate_totals
        return JsonResponse({"success": True, "message": "Ligne supprimée avec succès"})
    except Exception as e:
        return JsonResponse({"success": False, "error": f"Erreur lors de la suppression: {str(e)}"})

@csrf_exempt
def add_payment_mode(request):
    if request.method == 'POST':
        form = PaymentModeForm(request.POST)
        if form.is_valid():
            form.save()
            log_action(request.user, form.instance, 'creation')
    return redirect(reverse('purchases_configuration') + '?success=1')

@csrf_exempt
def delete_payment_mode(request, id=None):
    if request.method == 'POST':
        mode_id = id or request.POST.get('id')
        if not mode_id:
            return JsonResponse({'success': False, 'error': 'ID manquant.'})
        try:
            payment_mode = PaymentMode.objects.get(id=mode_id)
            payment_mode.delete()
            log_action(request.user, payment_mode, 'suppression')
            return JsonResponse({'success': True})
        except PaymentMode.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Mode de paiement introuvable.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Requête invalide.'})

@csrf_exempt
def confirm_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(PurchaseOrder, pk=order_id)
        if order.state == 'draft':
            data = json.loads(request.body)
            supplier_ref = data.get('supplier_ref')
            payment_mode_id = data.get('payment_mode_id')
            order.supplier_ref = supplier_ref or ''
            if payment_mode_id:
                payment_mode = get_object_or_404(PaymentMode, pk=payment_mode_id)
                order.payment_mode = payment_mode
            if order.name.startswith('PR-'):
                order.name = order.name.replace('PR-', 'PO-', 1)
            order.state = 'confirmed'
            order.save()
            log_action(request.user, order, 'confirmation')
            User = get_user_model()
            if request.user.is_authenticated:
                created_by = request.user
            else:
                try:
                    created_by = User.objects.filter(is_superuser=True).first() or User.objects.first()
                except Exception:
                    created_by = None
            if not created_by:
                return JsonResponse({'success': False, 'error': "Aucun utilisateur authentifié pour créer le mouvement de stock."})
            try:
                reception_type = OperationType.objects.filter(label__icontains='réception').first()
                if not reception_type:
                    return JsonResponse({'success': False, 'error': "Type d'opération 'Réception' introuvable."})
                next_id = (StockMove.objects.aggregate(max_id=models.Max('move_id'))['max_id'] or 0) + 1
                reference = f"STMV-{next_id:04d}"
                stock_move = StockMove.objects.create(
                    supplier=order.partner,
                    reference=reference,
                    state='draft',
                    operation_type=reception_type,
                    created_by=created_by,
                    scheduled_date=order.date_order
                )
                log_action(request.user, stock_move, 'creation')
                for line in order.order_lines.all():
                    line_stock_move = LineStockMove.objects.create(
                        move=stock_move,
                        product=line.product,
                        quantity_demanded=line.product_qty,
                        uom=line.product_uom,
                    )
                    log_action(request.user, line_stock_move, 'creation')  # Log LineStockMove creation
            except Exception as e:
                import traceback
                print(f"Erreur création StockMove: {e}")
                traceback.print_exc()
                return JsonResponse({'success': False, 'error': f"Erreur création StockMove: {e}"})
            return JsonResponse({'success': True, 'redirect': '/purchases/orders'})
        return JsonResponse({'success': False, 'error': 'Commande non en brouillon.'})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée.'})

def increment_reference(ref):
    match = re.match(r"^(PR|PO|BO)-(\d+)$", ref)
    if match:
        prefix, number = match.groups()
        new_number = int(number) + 1
        return f"{prefix}-{new_number:06d}"
    return f"{ref}-1"

@csrf_exempt
@transaction.atomic
def duplicate_order(request, order_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_supplier_id = data.get('supplier_id')
        original_order = get_object_or_404(PurchaseOrder, pk=order_id)
        new_supplier = get_object_or_404(Supplier, pk=new_supplier_id)
        new_ref = increment_reference(original_order.name)
        duplicated_order = PurchaseOrder.objects.create(
            name=new_ref,
            partner=new_supplier,
            date_order=original_order.date_order,
            currency=original_order.currency,
            payment_mode=original_order.payment_mode,
            amount_untaxed=Decimal('0.00'),
            amount_tax=Decimal('0.00'),
            amount_total=Decimal('0.00'),
            invoice_status='to_invoice',
            date_planned=original_order.date_planned,
            notes=original_order.notes,
            state='draft',
        )
        log_action(request.user, duplicated_order, 'creation')  # Log PurchaseOrder creation
        for line in original_order.order_lines.all():
            tax_amount = Decimal('0.00')
            if line.tax and hasattr(line.tax, 'valeur'):
                tax_amount = line.price_subtotal * (Decimal(str(line.tax.valeur)) / Decimal('100.0'))
            new_line = PurchaseOrderLine.objects.create(
                order=duplicated_order,
                product=line.product,
                product_qty=line.product_qty,
                price_unit=line.price_unit,
                price_subtotal=line.price_subtotal,
                product_uom=line.product_uom,
                tax=line.tax,
                name=line.name
            )
            log_action(request.user, new_line, 'creation')  # Log PurchaseOrderLine creation
            duplicated_order.amount_untaxed += line.price_subtotal
            duplicated_order.amount_tax += tax_amount
        duplicated_order.amount_total = duplicated_order.amount_untaxed + duplicated_order.amount_tax
        duplicated_order.save()
        log_action(request.user, duplicated_order, 'modification')  # Log PurchaseOrder update
        return JsonResponse({'success': True, 'order_id': duplicated_order.id})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

def delete_convention_type(request, id):
    convention_type = get_object_or_404(ConventionType, id=id)
    convention_type.delete()
    log_action(request.user, convention_type, 'suppression')
    return redirect('purchases_configuration')

def convention_list(request):
    conventions = Convention.objects.all().select_related('partner', 'convention_type', 'currency')
    suppliers = Supplier.objects.all()
    convention_types = ConventionType.objects.all()
    products = Product.objects.all()
    taxes = Tax.objects.all()
    currencies = Currency.objects.all()
    context = {
        'conventions': conventions,
        'suppliers': suppliers,
        'convention_types': convention_types,
        'products': products,
        'taxes': taxes,
        'currencies': currencies,
        'page_title': 'Conventions'
    }
    return render(request, 'conventions.html', context)



@transaction.atomic
def create_convention(request):
    if request.method == 'POST':
        try:
            supplier_id = request.POST.get('partner')
            convention_type_id = request.POST.get('convention_type')
            date_start = request.POST.get('date_start')
            date_end = request.POST.get('date_end')
            general_conditions = request.POST.get('general_conditions', '')
            notes = request.POST.get('notes', '')
            attachment = request.FILES.get('attachments')
            currency_id = request.POST.get('currency')

            if not all([supplier_id, convention_type_id, date_start, date_end, currency_id]):
                return JsonResponse({'success': False, 'message': 'Tous les champs requis doivent être remplis.'}, status=400)

            last_convention = Convention.objects.order_by('-id').first()
            next_id = (last_convention.id + 1) if last_convention else 1
            reference = f'BO-{next_id:06d}'

            supplier = get_object_or_404(Supplier, pk=supplier_id)
            convention_type = get_object_or_404(ConventionType, pk=convention_type_id)
            currency = get_object_or_404(Currency, pk=currency_id)

            convention = Convention.objects.create(
                name=reference,
                partner=supplier,
                convention_type=convention_type,
                date_start=date_start,
                date_end=date_end,
                general_conditions=general_conditions,
                attachments=attachment,
                notes=notes,
                amount_untaxed=0,
                amount_tax=0,
                amount_total=0,
                currency=currency,
            )
            log_action(request.user, convention, 'creation')

            products = request.POST.getlist('product[]')
            quantities = request.POST.getlist('quantity[]')
            unit_prices = request.POST.getlist('unit_price[]')
            taxes = request.POST.getlist('tax[]')

            if not products or not any(products):
                return JsonResponse({'success': False, 'message': 'Vous devez ajouter au moins une ligne de convention.'}, status=400)

            for i in range(len(products)):
                product_id = products[i]
                if not product_id:
                    continue
                product = Product.objects.filter(pk=product_id).first()
                if not product:
                    return JsonResponse({'success': False, 'message': f"Produit avec l'ID {product_id} introuvable."}, status=400)
                try:
                    qty = Decimal(quantities[i])
                    price_unit = Decimal(unit_prices[i])
                    if qty <= 0 or price_unit < 0:
                        return JsonResponse({'success': False, 'message': 'La quantité doit être positive et le prix unitaire ne peut pas être négatif.'}, status=400)
                    subtotal = qty * price_unit
                    tax_obj = Tax.objects.filter(pk=taxes[i]).first() if taxes[i] else None
                    tax_val = (subtotal * Decimal(tax_obj.valeur) / 100) if tax_obj else 0
                    line = ConventionLine.objects.create(
                        convention=convention,
                        product=product,
                        product_qty=qty,
                        price_unit=price_unit,
                        price_subtotal=subtotal,
                        tax=tax_obj,
                        name=product.name
                    )
                    log_action(request.user, line, 'creation')
                    convention.amount_untaxed += subtotal
                    convention.amount_tax += tax_val
                except (ValueError, InvalidOperation):
                    return JsonResponse({'success': False, 'message': f"Erreur dans les données de la ligne {i+1} : quantité ou prix invalide."}, status=400)

            convention.amount_total = convention.amount_untaxed + convention.amount_tax
            convention.save()
            log_action(request.user, convention, 'modification')

            return JsonResponse({'success': True, 'message': 'Convention créée avec succès.'}, status=200)

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erreur serveur : {str(e)}'}, status=500)

    suppliers = Supplier.objects.all()
    convention_types = ConventionType.objects.all()
    products = Product.objects.all()
    taxes = Tax.objects.all()
    currencies = Currency.objects.all()
    last = Convention.objects.order_by('-id').first()
    ref = f'BO-{(last.id + 1) if last else 1:06d}'
    return render(request, 'conventions.html', {
        'suppliers': suppliers,
        'convention_types': convention_types,
        'products': products,
        'taxes': taxes,
        'currencies': currencies,
        'page_title': 'Créer une Convention',
        'reference': ref,
    })

def delete_convention(request, pk):
    if request.method == 'POST':
        try:
            convention = get_object_or_404(Convention, pk=pk)
            # Log deletion of associated ConventionLine instances
            convention_lines = ConventionLine.objects.filter(convention=convention)
            for line in convention_lines:
                log_action(request.user, line, 'suppression')
            convention.delete()
            log_action(request.user, convention, 'suppression')
            return JsonResponse({'success': True, 'message': 'Convention supprimée avec succès.'}, status=200)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erreur lors de la suppression : {str(e)}'}, status=500)
    else:
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'}, status=405)

def convention_detail_json(request, convention_id):
    convention = get_object_or_404(Convention, pk=convention_id)
    partner = convention.partner
    lines = convention.convention_lines.all()
    convention_data = {
        'name': convention.name,
        'partner': {
            'name': partner.name if partner else 'N/A',
            'city': partner.city.name if partner and partner.city else 'N/A',
            'address': partner.street if partner else 'N/A',
            'email': partner.email if partner else 'N/A',
        },
        'type': convention.convention_type.libelle if convention.convention_type else 'N/A',
        'date_start': convention.date_start.strftime('%Y-%m-%d') if convention.date_start else 'N/A',
        'date_end': convention.date_end.strftime('%Y-%m-%d') if convention.date_end else 'N/A',
        'general_conditions': convention.general_conditions,
        'state': convention.get_state_display(),
        'amount_untaxed': str(convention.amount_untaxed),
        'amount_tax': str(convention.amount_tax),
        'amount_total': str(convention.amount_total),
        'notes': convention.notes,
        'currency': convention.currency.abreviation if convention.currency else 'N/A',
    }
    lines_data = [
        {
            'name': line.name,
            'qty': line.product_qty,
            'unit_price': str(line.price_unit),
            'subtotal': str(line.price_subtotal),
            'tax': f"{line.tax.libelle} ({line.tax.valeur}%)" if line.tax else "Sans taxe",
            'tax_amount': str(line.price_subtotal * Decimal(line.tax.valeur) / 100 if line.tax else 0),
            'total_ttc': str(line.price_subtotal + (line.price_subtotal * Decimal(line.tax.valeur) / 100 if line.tax else 0)),
        }
        for line in lines
    ]
    return JsonResponse({
        'convention': convention_data,
        'lines': lines_data
    })

def generate_convention_pdf(request, convention_id):
    convention = get_object_or_404(Convention, pk=convention_id)
    json_data = convention_detail_json(request, convention_id).content
    context = json.loads(json_data)
    html_string = render_to_string('convention_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="convention_{context["convention"]["name"]}.pdf"'
    HTML(string=html_string).write_pdf(response)
    log_action(request.user, convention, 'impression')
    return response

@csrf_exempt
def confirm_convention(request, convention_id):
    if request.method == 'POST':
        convention = get_object_or_404(Convention, pk=convention_id)
        if convention.state == 'draft':
            convention.state = 'confirmed'
            convention.save()
            log_action(request.user, convention, 'confirmation')
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': "La convention n'est pas en brouillon."})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée.'})

@csrf_exempt
def edit_convention(request, convention_id):
    convention = get_object_or_404(Convention, id=convention_id)
    ConventionLineFormSet = modelformset_factory(
        ConventionLine,
        form=ConventionLineForm,
        extra=0,
        can_delete=True,
    )
    if request.method == 'POST':
        form = ConventionForm(request.POST, request.FILES, instance=convention)
        formset = ConventionLineFormSet(request.POST, prefix='lines', queryset=convention.convention_lines.all())
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                convention = form.save()
                log_action(request.user, convention, 'modification')  # Log Convention modification
                for form in formset:
                    if form.cleaned_data:
                        if form.cleaned_data.get('DELETE'):
                            if form.instance.pk:
                                log_action(request.user, form.instance, 'suppression')  # Log ConventionLine deletion
                                form.instance.delete()
                            continue
                        if not form.cleaned_data.get('product'):
                            continue
                        line = form.save(commit=False)
                        line.convention = convention
                        line.price_subtotal = Decimal(line.product_qty) * Decimal(line.price_unit or 0)
                        if not line.name:
                            line.name = str(line.product)
                        line.save()
                        log_action(request.user, line, 'modification' if form.instance.pk else 'creation')  # Log line modification or creation
                recalculate_convention_totals(request, convention)  # Pass request to recalculate_convention_totals
                messages.success(request, 'Convention modifiée avec succès.')
                return redirect('convention_list')
        else:
            messages.error(request, 'Erreur dans le formulaire.')
    else:
        form = ConventionForm(instance=convention)
        formset = ConventionLineFormSet(queryset=convention.convention_lines.all(), prefix='lines')
    context = {
        'form': form,
        'formset': formset,
        'convention': convention,
        'suppliers': Supplier.objects.all(),
        'convention_types': ConventionType.objects.all(),
        'products': Product.objects.all(),
        'units': UnitOfMesure.objects.all(),
        'taxes': Tax.objects.all(),
        'payment_modes': PaymentMode.objects.all(),
        'currencies': Currency.objects.all(),
        'page_title': f'Modifier la convention {convention.name}',
    }
    return render(request, 'edit_convention.html', context)

def recalculate_convention_totals(request, convention):
    total_untaxed = Decimal('0')
    total_tax = Decimal('0')
    for line in convention.convention_lines.all():
        total_untaxed += line.price_subtotal or 0
        if line.tax:
            total_tax += (line.price_subtotal * Decimal(line.tax.valeur)) / 100
    convention.amount_untaxed = total_untaxed
    convention.amount_tax = total_tax
    convention.amount_total = total_untaxed + total_tax
    convention.save()
    log_action(request.user, convention, 'modification')  # Log Convention update

@require_http_methods(["POST"])
@csrf_exempt
def delete_convention_line(request, line_id):
    try:
        line = get_object_or_404(ConventionLine, id=line_id)
        convention = line.convention
        log_action(request.user, line, 'suppression')  # Log ConventionLine deletion
        line.delete()
        recalculate_convention_totals(request, convention)  # Pass request to recalculate_convention_totals
        return JsonResponse({'success': True, 'message': 'Ligne supprimée avec succès'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@transaction.atomic
def duplicate_convention(request, convention_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_supplier_id = data.get('supplier_id')
        original = get_object_or_404(Convention, pk=convention_id)
        new_supplier = get_object_or_404(Supplier, pk=new_supplier_id)
        new_ref = increment_reference(original.name)
        new_convention = Convention.objects.create(
            name=new_ref,
            partner=new_supplier,
            convention_type=original.convention_type,
            date_start=original.date_start,
            date_end=original.date_end,
            general_conditions=original.general_conditions,
            notes=original.notes,
            amount_untaxed=0,
            amount_tax=0,
            amount_total=0,
            state='draft',
            currency=original.currency
        )
        log_action(request.user, new_convention, 'creation')  # Log Convention creation
        for line in original.convention_lines.all():
            new_line = ConventionLine.objects.create(
                convention=new_convention,
                product=line.product,
                product_qty=line.product_qty,
                price_unit=line.price_unit,
                price_subtotal=line.price_subtotal,
                tax=line.tax,
                name=line.name
            )
            log_action(request.user, new_line, 'creation')  # Log ConventionLine creation
            tax_val = line.price_subtotal * Decimal(line.tax.valeur) / 100 if line.tax else 0
            new_convention.amount_untaxed += line.price_subtotal
            new_convention.amount_tax += tax_val
        new_convention.amount_total = new_convention.amount_untaxed + new_convention.amount_tax
        new_convention.save()
        log_action(request.user, new_convention, 'modification')  # Log Convention update
        return JsonResponse({'success': True, 'convention_id': new_convention.id})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

@require_http_methods(["POST"])
def convention_list_filtered(request):
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    supplier = request.POST.get('supplier')
    state = request.POST.get('status')
    conventions = Convention.objects.all().select_related('partner', 'convention_type')
    if start_date:
        conventions = conventions.filter(date_start__gte=start_date)
    if end_date:
        conventions = conventions.filter(date_end__lte=end_date)
    if supplier:
        conventions = conventions.filter(partner_id=supplier)
    if state:
        conventions = conventions.filter(state=state)
    results = [
        {
            'id': c.id,
            'name': c.name,
            'partner_name': c.partner.name,
            'type': c.convention_type.libelle,
            'date_start': c.date_start.strftime('%Y-%m-%d'),
            'date_end': c.date_end.strftime('%Y-%m-%d'),
            'state': c.state,
            'state_display': c.get_state_display(),
            'amount_total': float(c.amount_total),
        }
        for c in conventions
    ]
    return JsonResponse({'conventions': results})



def purchases_product_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
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
    if category_id:
        products = products.filter(categ_id=category_id)
    paginator = Paginator(products, 5)
    page_number = request.GET.get('page')
    if query and not page_number:
        page_number = 1
    page_obj = paginator.get_page(page_number)
    product_locations_json = {}
    for product in page_obj:
        product_locations = list(ProductLocation.objects.filter(product=product).values('location_id', 'quantity_stored'))
        for loc in product_locations:
            loc['quantity_stored'] = float(loc['quantity_stored'])
        product_locations_json[product.pk] = json.dumps(product_locations)
    form = ProductForm()
    context = {
        'page_obj': page_obj,
        'form': form,
        'page_title': 'Produits',
        'product': None,
        'locations': StockLocation.objects.all(),
        'product_locations': json.dumps([]),
        'product_locations_json': product_locations_json,
        'product_types': ProductType.objects.all(),
        'categories': Category.objects.all(),
    }
    return render(request, 'purchases_products.html', context)

def generate_product_reference():
    last_product = Product.objects.filter(default_code__startswith='PDT-').order_by('-product_id').first()
    if last_product and last_product.default_code:
        try:
            last_number = int(last_product.default_code.split('-')[-1])
        except ValueError:
            last_number = 0
    else:
        last_number = 0
    return f'PDT-{last_number + 1:05d}'

@csrf_exempt
@transaction.atomic
def purchases_product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.default_code = generate_product_reference()
            product.save()
            log_action(request.user, product, 'creation')
            ProductLocation.objects.filter(product=product).delete()
            locations_json = request.POST.get('locations_json', '[]')
            try:
                locations = json.loads(locations_json)
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Erreur dans les données des emplacements.'
                }, status=400)
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
                        product_location = ProductLocation.objects.create(
                            product=product,
                            location=location,
                            quantity_stored=quantity,
                            last_count_date=timezone.now().date()
                        )
                        log_action(request.user, product_location, 'creation')
                        total += quantity
                    except (StockLocation.DoesNotExist, ValueError) as e:
                        return JsonResponse({
                            'success': False,
                            'error': f"Emplacement {location_id} invalide ou quantité incorrecte: {str(e)}"
                        }, status=400)
            product.total_quantity_cached = total
            product.save()
            return JsonResponse({
                'success': True,
                'message': 'Produit créé avec succès !'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Erreur dans le formulaire produit.'
            }, status=400)
    form = ProductForm()
    products = Product.objects.all().order_by('-product_id')
    paginator = Paginator(products, 5)
    page_number = request.GET.get('page') or 1
    page_obj = paginator.get_page(page_number)
    product_locations_json = {}
    for prod in page_obj:
        prod_locations = list(ProductLocation.objects.filter(product=prod).values('location_id', 'quantity_stored'))
        for loc in prod_locations:
            loc['quantity_stored'] = float(loc['quantity_stored'])
        product_locations_json[prod.pk] = json.dumps(prod_locations)
    return render(request, 'purchases_products.html', {
        'form': form,
        'page_title': 'Ajouter un Produit',
        'product': None,
        'locations': StockLocation.objects.all(),
        'product_locations': json.dumps([]),
        'product_locations_json': product_locations_json,
        'products': products,
        'page_obj': page_obj,
        'product_types': ProductType.objects.all(),
        'categories': Category.objects.all(),
    })

@csrf_exempt
@transaction.atomic
def purchases_product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            log_action(request.user, product, 'modification')
            existing_locations = list(ProductLocation.objects.filter(product=product).values('product_location_id', 'location_id', 'quantity_stored'))
            existing_locations_dict = {loc['product_location_id']: loc for loc in existing_locations}
            locations_json = request.POST.get('locations_json', '[]')
            try:
                new_locations = json.loads(locations_json)
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Erreur dans les données des emplacements.'
                }, status=400)
            total = 0
            new_locations_dict = {loc['location_id']: loc for loc in new_locations if loc.get('location_id') and loc.get('quantity_stored')}
            for existing_loc in existing_locations:
                existing_loc_id = existing_loc['product_location_id']
                existing_location_id = existing_loc['location_id']
                existing_quantity = float(existing_loc['quantity_stored'])
                if existing_location_id in new_locations_dict:
                    new_loc = new_locations_dict[existing_location_id]
                    new_quantity = float(new_loc['quantity_stored'])
                    if new_quantity != existing_quantity:
                        product_location = ProductLocation.objects.get(product_location_id=existing_loc_id)
                        log_action(request.user, product_location, 'modification', details=f"Quantity changed from {existing_quantity} to {new_quantity}")
                    del new_locations_dict[existing_location_id]
                else:
                    product_location = ProductLocation.objects.get(product_location_id=existing_loc_id)
                    log_action(request.user, product_location, 'suppression')
            ProductLocation.objects.filter(product=product).delete()
            for loc in new_locations:
                location_id = loc.get('location_id')
                quantity_stored = loc.get('quantity_stored')
                if location_id and quantity_stored:
                    try:
                        location = StockLocation.objects.get(pk=location_id)
                        quantity = float(quantity_stored)
                        if quantity < 0:
                            raise ValueError("La quantité ne peut pas être négative.")
                        product_location = ProductLocation.objects.create(
                            product=product,
                            location=location,
                            quantity_stored=quantity,
                            last_count_date=timezone.now().date()
                        )
                        log_action(request.user, product_location, 'creation')
                        total += quantity
                    except (StockLocation.DoesNotExist, ValueError) as e:
                        return JsonResponse({
                            'success': False,
                            'error': f"Emplacement {location_id} invalide ou quantité incorrecte: {str(e)}"
                        }, status=400)
            product.total_quantity_cached = total
            product.save()
            log_action(request.user, product, 'modification')
            return JsonResponse({
                'success': True,
                'message': 'Produit et emplacements modifiés avec succès !'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Erreur dans le formulaire produit.'
            }, status=400)
    form = ProductForm(instance=product)
    product_locations = list(ProductLocation.objects.filter(product=product).values('location_id', 'quantity_stored'))
    for loc in product_locations:
        loc['quantity_stored'] = float(loc['quantity_stored'])
    product_locations_json = json.dumps(product_locations)
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
    return render(request, 'purchases_products.html', {
        'form': form,
        'page_title': 'Modifier un Produit',
        'product': product,
        'locations': StockLocation.objects.all(),
        'product_locations': product_locations_json,
        'products': products,
        'page_obj': page_obj,
        'product_locations_json': product_locations_dict,
        'product_types': ProductType.objects.all(),
        'categories': Category.objects.all(),
    })

@csrf_exempt
def purchases_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        try:
            product_locations = ProductLocation.objects.filter(product=product)
            for loc in product_locations:
                log_action(request.user, loc, 'suppression')
            product_locations.delete()
            log_action(request.user, product, 'suppression')
            product.delete()
            return JsonResponse({
                'success': True,
                'message': 'Produit supprimé avec succès !'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erreur lors de la suppression du produit: {str(e)}'
            }, status=400)
    return JsonResponse({
        'success': False,
        'error': 'Méthode non autorisée'
    }, status=405)



@require_http_methods(["GET"])
def product_order_history(request, pk):
    try:
        product = get_object_or_404(Product, pk=pk)
        # Filtre ajouté : seulement les commandes passées ('purchase' et 'done')
        order_lines = PurchaseOrderLine.objects.filter(
            product=product,
            order__state__in=('purchase', 'confirmed')
        ).select_related('order__currency', 'order')
        
        total_orders = order_lines.count()
        # Turnover mis à jour avec le filtre
        turnover = sum(float(line.price_subtotal) for line in order_lines if line.price_subtotal)
        
        # Progression des prix mise à jour avec le filtre
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
        # Formatage avec deux décimales
        price_data = ["%.2f" % float(entry['avg_price']) if entry['avg_price'] else "0.00" for entry in price_progression]
        turnover_data = ["%.2f" % float(entry['total_turnover']) if entry['total_turnover'] else "0.00" for entry in price_progression]
        
        order_details = [
            {
                'order_id': line.order.id,
                'order_name': line.order.name,
                'date_order': line.order.date_order.strftime('%Y-%m-%d') if line.order.date_order else 'N/A',
                # Formatage avec deux décimales
                'unit_price': "%.2f" % float(line.price_unit) if line.price_unit else "0.00",
                'quantity': float(line.product_qty) if line.product_qty else 0,
                'subtotal': "%.2f" % float(line.price_subtotal) if line.price_subtotal else "0.00",
                'currency': 'MAD',
                'state': line.order.get_state_display()
            }
            for line in order_lines
        ]
        
        return JsonResponse({
            'success': True,
            'product_name': product.name,
            'total_orders': total_orders,
            'turnover': "%.2f" % turnover,  # Formatage du turnover total
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
def product_order_history_pdf(request, pk):
    try:
        product = get_object_or_404(Product, pk=pk)
        # Filtre ajouté : seulement les commandes passées ('purchase' et 'done')
        order_lines = PurchaseOrderLine.objects.filter(
            product=product,
            order__state__in=('purchase', 'confirmed')
        ).select_related('order__currency', 'order')
        
        total_orders = order_lines.count()
        # Turnover mis à jour avec le filtre
        turnover = sum(float(line.price_subtotal) for line in order_lines if line.price_subtotal)
        
        # Progression des prix mise à jour avec le filtre
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
                # Formatage avec deux décimales
                'avg_price': "%.2f" % float(entry['avg_price']) if entry['avg_price'] else "0.00",
                'total_turnover': "%.2f" % float(entry['total_turnover']) if entry['total_turnover'] else "0.00"
            }
            for entry in price_progression
        ]
        
        order_details = [
            {
                'order_name': line.order.name,
                'date_order': line.order.date_order.strftime('%Y-%m-%d') if line.order.date_order else 'N/A',
                # Formatage avec deux décimales
                'unit_price': "%.2f" % float(line.price_unit) if line.price_unit else "0.00",
                'quantity': float(line.product_qty) if line.product_qty else 0,
                'subtotal': "%.2f" % float(line.price_subtotal) if line.price_subtotal else "0.00",
                'currency': 'MAD',
                'state': line.order.get_state_display()
            }
            for line in order_lines
        ]
        
        context = {
            'product': {
                'name': product.name,
                'default_code': product.default_code or 'N/A',
                'category': product.categ.label if product.categ else 'N/A',
                'uom': product.uom.label if product.uom else 'N/A'
            },
            'total_orders': total_orders,
            'turnover': "%.2f" % turnover,  # Formatage du turnover total
            'price_data': price_data,
            'orders': order_details,
            'current_date': timezone.now().strftime('%Y-%m-%d'),
        }
        html_string = render_to_string('product_order_history_pdf.html', context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="order_history_{product.name.replace(" ", "_")}.pdf"'
        HTML(string=html_string).write_pdf(response)
        log_action(request.user, product, 'impression')
        return response
    except Exception as e:
        return HttpResponse(f"Erreur lors de la génération du PDF : {str(e)}", status=500)

def purchases_dashboard(request):
    total_orders = PurchaseOrder.objects.count()
    total_conventions = Convention.objects.count()
    total_suppliers = Supplier.objects.count()
    total_order_amount = PurchaseOrder.objects.aggregate(Sum('amount_total'))['amount_total__sum'] or Decimal('0.00')
    orders = PurchaseOrder.objects.all().select_related('partner', 'currency').order_by('-date_order')[:5]
    conventions = Convention.objects.all().select_related('partner', 'convention_type', 'currency').order_by('-date_start')[:5]
    suppliers = Supplier.objects.all()
    purchase_order_states = PurchaseOrder.STATE_CHOICES
    return render(request, 'purchases_dashboard.html', {
        'total_orders': total_orders,
        'total_conventions': total_conventions,
        'total_suppliers': total_suppliers,
        'total_order_amount': "%.2f" % float(total_order_amount),  # Formatage ajouté
        'orders': orders,
        'conventions': conventions,
        'suppliers': suppliers,
        'purchase_order_states': purchase_order_states,
        'page_title': 'Tableau de bord - Achats'
    })
@require_http_methods(["GET"])
def orders_by_state(request):
    try:
        orders_by_state = PurchaseOrder.objects.values('state').annotate(count=Count('id')).order_by('state')
        labels = [dict(PurchaseOrder.STATE_CHOICES).get(entry['state'], entry['state']) for entry in orders_by_state]
        data = [entry['count'] for entry in orders_by_state]
        return JsonResponse({'labels': labels, 'data': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def orders_evolution(request):
    try:
        from datetime import timedelta
        end_date = timezone.now()
        start_date = end_date - timedelta(days=365)
        orders_by_month = (
            PurchaseOrder.objects
            .filter(date_order__gte=start_date, date_order__lte=end_date)
            .annotate(month=TruncMonth('date_order'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        labels = [entry['month'].strftime('%Y-%m') for entry in orders_by_month]
        data = [entry['count'] for entry in orders_by_month]
        return JsonResponse({'labels': labels, 'data': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)