from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone
from django.template.loader import render_to_string
from .models import Vehicule, Marque, Modele, Entretien, Affectation, ContractType, Contract, Provider, StatutVehicule, TypeEntretien, StatutEntretien, TypeVehicule 
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_http_methods
from django.http import JsonResponse, HttpResponse
from apps.hr.models import Employee
from django.views.decorators.gzip import gzip_page
from django.db import IntegrityError
from django import template
from django.views.decorators.cache import cache_page
import json
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import logging
from django.db.models import Count, Avg, Max, Min, Sum, F
from django.db.models.functions import ExtractMonth
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

logger = logging.getLogger(__name__)
register = template.Library()

# =============================================
# VEHICLE MANAGEMENT (PARC AUTO) CRUD OPERATIONS
# =============================================

def parcauto_list(request):
    """
    List all vehicles with filtering and pagination capabilities
    Handles both regular requests and AJAX requests for table updates
    """
    try:
        query = request.GET.get('q', '').strip()
        marque_id = request.GET.get('marque_id')

        vehicules = Vehicule.objects.all()
        
        if query:
            vehicules = vehicules.filter(immatriculation__icontains=query)
        if marque_id:
            vehicules = vehicules.filter(marque__id=marque_id)
        
        vehicules = vehicules.order_by('-annee')
        
        # Pagination setup
        items_per_page = request.GET.get('items_per_page', '5')
        try:
            items_per_page = int(items_per_page)
            if items_per_page not in [5, 10, 25]:
                items_per_page = 5
        except (ValueError, TypeError):
            items_per_page = 5
        
        paginator = Paginator(vehicules, items_per_page)
        page_number = request.GET.get('page')
        
        try:
            vehicules = paginator.page(page_number)
        except PageNotAnInteger:
            vehicules = paginator.page(1)
        except EmptyPage:
            vehicules = paginator.page(paginator.num_pages)

        context = {
            'vehicules': vehicules,
            'query': query,
            'today': timezone.now().date(),
            'types': dict(Vehicule._meta.get_field('type').choices),
            'statuts': dict(Vehicule._meta.get_field('statut').choices),
            'marques': Marque.objects.all(),
            'modeles': Modele.objects.all(),
        }

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html_content = render_to_string('parcauto_index.html', context)
            import re
            match = re.search(r'<tbody id="vehicules-table">(.*?)</tbody>', html_content, re.DOTALL)
            if match:
                return render(request, 'empty_tbody.html', {'tbody_html': match.group(1)})
            else:
                return HttpResponse('<tr><td colspan="10" class="text-center text-danger">Erreur: Impossible de trouver le tableau</td></tr>')

        return render(request, 'parcauto_index.html', context)

    except Exception as e:
        import traceback
        traceback.print_exc()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=500)
        raise

def parcauto_create(request):
    """Create a new vehicle with validation for required fields and immatriculation uniqueness"""
    try:
        immatriculation = request.POST.get('immatriculation')
        marque_id = request.POST.get('marque')
        modele_id = request.POST.get('modele')
        annee = request.POST.get('annee')
        type_vehicule = request.POST.get('type')
        statut = request.POST.get('statut')
        kilometrage = request.POST.get('kilometrage_actuel')
        date_achat = request.POST.get('date_achat')
        date_mise_service = request.POST.get('date_mise_service')

        # Basic field validation
        if not all([immatriculation, marque_id, modele_id, annee, type_vehicule, statut, kilometrage, date_achat, date_mise_service]):
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
            return redirect('parcauto_home')

        try:
            marque = Marque.objects.get(id=marque_id)
            modele = Modele.objects.get(id=modele_id)
        except (Marque.DoesNotExist, Modele.DoesNotExist):
            messages.error(request, 'Marque ou modèle invalide.')
            return redirect('parcauto_home')

        # Attempt to create the vehicle
        try:
            Vehicule.objects.create(
                immatriculation=immatriculation.strip().upper(),
                marque=marque,
                modele=modele,
                annee=int(annee),
                type=type_vehicule,
                statut=statut,
                kilometrage_actuel=int(kilometrage),
                date_achat=date_achat,
                date_mise_service=date_mise_service
            )
            messages.success(request, f'Véhicule "{immatriculation}" ajouté avec succès !')
        except IntegrityError as e:
            if 'immatriculation' in str(e).lower() or 'unique constraint' in str(e).lower():
                 messages.error(request, f'Erreur : Un véhicule avec l\'immatriculation "{immatriculation}" existe déjà.')
                 logger.warning(f"Tentative d'ajout d'un doublon d'immatriculation: {immatriculation}")
            else:
                 logger.error(f"Erreur d'intégrité inattendue lors de la création du véhicule: {e}")
                 messages.error(request, f'Erreur lors de l\'ajout du véhicule : {str(e)}')
        except ValueError as e:
             messages.error(request, f'Données invalides fournies (année ou kilométrage).')
             logger.error(f"Erreur de conversion de données lors de la création: {e}")

        return redirect('parcauto_home')

    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'ajout du véhicule: {e}", exc_info=True)
        messages.error(request, f'Erreur lors de l\'ajout du véhicule : {str(e)}')
        return redirect('parcauto_home')

def parcauto_update(request):
    """Update an existing vehicle with validation for required fields and immatriculation uniqueness"""
    try:
        vehicule_id = request.POST.get('voiture_id') or request.POST.get('vehicule_id')
        immatriculation = request.POST.get('immatriculation')
        marque_id = request.POST.get('marque')
        modele_id = request.POST.get('modele')
        annee = request.POST.get('annee')
        type_vehicule = request.POST.get('type')
        statut = request.POST.get('statut')
        kilometrage = request.POST.get('kilometrage_actuel')
        date_achat = request.POST.get('date_achat')
        date_mise_service = request.POST.get('date_mise_service')

        # Basic field validation
        if not all([vehicule_id, immatriculation, marque_id, modele_id, annee, type_vehicule, statut, kilometrage, date_achat, date_mise_service]):
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
            return redirect('parcauto_home')

        try:
            vehicule = Vehicule.objects.get(id=vehicule_id)
            marque = Marque.objects.get(id=marque_id)
            modele = Modele.objects.get(id=modele_id)
        except (Vehicule.DoesNotExist, Marque.DoesNotExist, Modele.DoesNotExist):
            messages.error(request, 'Véhicule, marque ou modèle introuvable.')
            return redirect('parcauto_home')

        # Check immatriculation conflict
        standardized_immat = immatriculation.strip().upper()
        if standardized_immat != vehicule.immatriculation and Vehicule.objects.filter(immatriculation=standardized_immat).exists():
             messages.error(request, f'Erreur : Un autre véhicule avec l\'immatriculation "{immatriculation}" existe déjà.')
             return redirect('parcauto_home')

        # Update vehicle fields
        vehicule.immatriculation = standardized_immat
        vehicule.marque = marque
        vehicule.modele = modele
        vehicule.annee = int(annee)
        vehicule.type = type_vehicule
        vehicule.statut = statut
        vehicule.kilometrage_actuel = int(kilometrage)
        vehicule.date_achat = date_achat
        vehicule.date_mise_service = date_mise_service

        # Attempt to save the vehicle
        try:
            vehicule.save()
            messages.success(request, f'Véhicule "{immatriculation}" modifié avec succès !')
        except IntegrityError as e:
            if 'immatriculation' in str(e).lower() or 'unique constraint' in str(e).lower():
                 messages.error(request, f'Erreur : Impossible de modifier. Un véhicule avec l\'immatriculation "{immatriculation}" existe déjà.')
                 logger.warning(f"Tentative de mise à jour vers un doublon d'immatriculation: {immatriculation} pour ID {vehicule_id}")
            else:
                 logger.error(f"Erreur d'intégrité inattendue lors de la mise à jour du véhicule ID {vehicule_id}: {e}")
                 messages.error(request, f'Erreur lors de la modification du véhicule : {str(e)}')
        except ValueError as e: 
             messages.error(request, f'Données invalides fournies (année ou kilométrage).')
             logger.error(f"Erreur de conversion de données lors de la mise à jour ID {vehicule_id}: {e}")

        return redirect('parcauto_home')

    except Exception as e: 
        logger.error(f"Erreur inattendue lors de la mise à jour du véhicule ID {vehicule_id}: {e}", exc_info=True)
        messages.error(request, f'Erreur lors de la modification du véhicule : {str(e)}')
        return redirect('parcauto_home')
    
def parcauto_delete(request):
    """Delete a vehicle record"""
    try:
        vehicule_id = request.POST.get('voiture_id') or request.POST.get('vehicule_id')
        if not vehicule_id:
            messages.error(request, 'ID du véhicule manquant.')
            return redirect('parcauto_home')

        try:
            vehicule = Vehicule.objects.get(id=vehicule_id)
            immatriculation = vehicule.immatriculation
            vehicule.delete()
            messages.success(request, f'Véhicule "{immatriculation}" supprimé avec succès !')
        except Vehicule.DoesNotExist:
            messages.error(request, 'Véhicule introuvable.')

        return redirect('parcauto_home')

    except Exception as e:
        messages.error(request, f'Erreur lors de la suppression du véhicule : {str(e)}')
        return redirect('parcauto_home')

# =============================================
# CONFIGURATION MANAGEMENT CRUD OPERATIONS
# =============================================

def configuration_list(request):
    """List all configuration items with pagination"""
    marques_per_page = request.GET.get('marques_per_page', 5)
    modeles_per_page = request.GET.get('modeles_per_page', 5)
    entretien_types_per_page = request.GET.get('entretien_types_per_page', 5)
    contract_types_per_page = request.GET.get('contract_types_per_page', 5)
    providers_per_page = request.GET.get('providers_per_page', 5)
    
    marques_page = request.GET.get('marques_page', 1)
    modeles_page = request.GET.get('modeles_page', 1)
    entretien_types_page = request.GET.get('entretien_types_page', 1)
    contract_types_page = request.GET.get('contract_types_page', 1)
    providers_page = request.GET.get('providers_page', 1)
    
    marques = Marque.objects.all().order_by('nom')
    marques_paginator = Paginator(marques, marques_per_page)
    marques = marques_paginator.page(marques_page)
    
    modeles = Modele.objects.select_related('marque').order_by('marque__nom', 'nom')
    modeles_paginator = Paginator(modeles, modeles_per_page)
    modeles = modeles_paginator.page(modeles_page)
    
    entretien_types = TypeEntretien.objects.all().order_by('nom')
    entretien_types_paginator = Paginator(entretien_types, entretien_types_per_page)
    entretien_types = entretien_types_paginator.page(entretien_types_page)
    
    contract_types = ContractType.objects.all().order_by('name')
    contract_types_paginator = Paginator(contract_types, contract_types_per_page)
    contract_types = contract_types_paginator.page(contract_types_page)
    
    providers = Provider.objects.all().order_by('name')
    providers_paginator = Paginator(providers, providers_per_page)
    providers = providers_paginator.page(providers_page)
    
    return render(request, 'parcauto_configuration.html', {
        'marques': marques,
        'modeles': modeles,
        'entretien_types': entretien_types,
        'contract_types': contract_types,
        'providers': providers,
    })

# Brand (Marque) CRUD operations
def marque_create(request):
    """Create a new vehicle brand"""
    try:
        nom = request.POST.get('nom_marque')
        logo = request.FILES.get('logo_marque')
        
        if not nom:
            messages.error(request, 'Le nom de la marque est obligatoire')
            return redirect('parcauto_configuration')
        
        if Marque.objects.filter(nom__iexact=nom).exists():
            messages.error(request, 'Cette marque existe déjà')
            return redirect('parcauto_configuration')
        
        marque = Marque(nom=nom)
        if logo:
            marque.logo = logo
        marque.save()
        
        messages.success(request, f'Marque "{nom}" ajoutée avec succès!')
        return redirect('parcauto_configuration')
    
    except Exception as e:
        messages.error(request, f'Erreur lors de la création de la marque: {str(e)}')
        return redirect('parcauto_configuration')

def marque_update(request, marque_id):
    """Update an existing vehicle brand"""
    try:
        nom = request.POST.get('nom_marque')
        logo = request.FILES.get('logo_marque')
        remove_logo = request.POST.get('remove_logo') == 'on'

        if not nom:
            messages.error(request, 'Données manquantes')
            return redirect('parcauto_configuration')

        try:
            marque = Marque.objects.get(id=marque_id)
        except Marque.DoesNotExist:
            messages.error(request, 'Marque introuvable')
            return redirect('parcauto_configuration')
        
        if Marque.objects.filter(nom__iexact=nom).exclude(id=marque_id).exists():
            messages.error(request, 'Une marque avec ce nom existe déjà')
            return redirect('parcauto_configuration')
        
        marque.nom = nom
        
        if remove_logo:
            marque.logo.delete(save=False)
        elif logo:
            marque.logo = logo
        
        marque.save()
        messages.success(request, 'Marque mise à jour avec succès!')
        return redirect('parcauto_configuration')
    
    except Exception as e:
        messages.error(request, f'Erreur lors de la modification: {str(e)}')
        return redirect('parcauto_configuration')
    
def marque_delete(request, marque_id):
    """Delete a vehicle brand if not in use"""
    try:
        try:
            marque = Marque.objects.get(id=marque_id)
            nom = marque.nom
            
            if hasattr(marque, 'modele_set') and marque.modele_set.exists():
                messages.error(request, f'Impossible de supprimer "{nom}" car elle est utilisée par des modèles')
                return redirect('parcauto_configuration')
            
            marque.delete()
            messages.success(request, f'Marque "{nom}" supprimée avec succès!')
        except Marque.DoesNotExist:
            messages.error(request, 'Marque introuvable')
        
        return redirect('parcauto_configuration')
    
    except Exception as e:
        messages.error(request, f'Erreur lors de la suppression: {str(e)}')
        return redirect('parcauto_configuration')

# Model (Modele) CRUD operations
def modele_create(request):
    """Create a new vehicle model"""
    try:
        nom = request.POST.get('nom_modele')
        marque_id = request.POST.get('marque_modele')
        
        if not (nom and marque_id):
            messages.error(request, 'Tous les champs sont obligatoires')
            return redirect('parcauto_configuration')
        
        try:
            marque = Marque.objects.get(id=marque_id)
        except Marque.DoesNotExist:
            messages.error(request, 'Marque sélectionnée invalide')
            return redirect('parcauto_configuration')
        
        if Modele.objects.filter(nom__iexact=nom, marque=marque).exists():
            messages.error(request, 'Ce modèle existe déjà pour cette marque')
            return redirect('parcauto_configuration')
        
        Modele.objects.create(nom=nom, marque=marque)
        messages.success(request, f'Modèle "{nom}" ajouté avec succès!')
        return redirect('parcauto_configuration')
    
    except Exception as e:
        messages.error(request, f'Erreur lors de la création du modèle: {str(e)}')
        return redirect('parcauto_configuration')
    
def modele_update(request, modele_id):
    """Update an existing vehicle model"""
    try:
        nom = request.POST.get('nom_modele')
        marque_id = request.POST.get('marque_modele')

        if not (nom and marque_id):
            messages.error(request, 'Données manquantes')
            return redirect('parcauto_configuration')

        try:
            modele = Modele.objects.get(id=modele_id)
            marque = Marque.objects.get(id=marque_id)
        except (Modele.DoesNotExist, Marque.DoesNotExist):
            messages.error(request, 'Modèle ou marque introuvable')
            return redirect('parcauto_configuration')
        
        if Modele.objects.filter(nom__iexact=nom, marque=marque).exclude(id=modele_id).exists():
            messages.error(request, 'Ce modèle existe déjà pour cette marque')
            return redirect('parcauto_configuration')
        
        modele.nom = nom
        modele.marque = marque
        modele.save()
        messages.success(request, 'Modèle mis à jour avec succès!')
        return redirect('parcauto_configuration')
    
    except Exception as e:
        messages.error(request, f'Erreur lors de la modification: {str(e)}')
        return redirect('parcauto_configuration')
    
def modele_delete(request, modele_id):
    """Delete a vehicle model if not in use"""
    try:
        try:
            modele = Modele.objects.get(id=modele_id)
            nom = modele.nom
            
            if modele.vehicule_set.exists():
                messages.error(request, f'Impossible de supprimer "{nom}" car il est utilisé par des véhicules')
                return redirect('parcauto_configuration')
            
            modele.delete()
            messages.success(request, f'Modèle "{nom}" supprimé avec succès!')
        except Modele.DoesNotExist:
            messages.error(request, 'Modèle introuvable')
        
        return redirect('parcauto_configuration')
    
    except Exception as e:
        messages.error(request, f'Erreur lors de la suppression: {str(e)}')
        return redirect('parcauto_configuration')

# Contract Type CRUD operations
def contract_type_create(request):
    """Create a new contract type"""
    try:
        name = request.POST.get('type_name')
        code = request.POST.get('type_code')
        description = request.POST.get('type_description')
        
        if not all([name, code]):
            messages.error(request, 'Name and code are required')
            return redirect('parcauto_configuration')
        
        if ContractType.objects.filter(code__iexact=code).exists():
            messages.error(request, 'A contract type with this code already exists')
            return redirect('parcauto_configuration')
            
        ContractType.objects.create(
            name=name,
            code=code,
            description=description
        )
        
        messages.success(request, 'Contract type created successfully')
        return redirect('parcauto_configuration')
        
    except Exception as e:
        messages.error(request, f'Error creating contract type: {str(e)}')
        return redirect('parcauto_configuration')

def contract_type_update(request, type_id):
    """Update an existing contract type"""
    try:
        name = request.POST.get('type_name')
        code = request.POST.get('type_code')
        description = request.POST.get('type_description')

        if not all([name, code]):
            messages.error(request, 'Missing required fields')
            return redirect('parcauto_configuration')

        contract_type = ContractType.objects.get(id=type_id)
        
        if ContractType.objects.filter(code__iexact=code).exclude(id=type_id).exists():
            messages.error(request, 'This code is already used by another contract type')
            return redirect('parcauto_configuration')
            
        contract_type.name = name
        contract_type.code = code
        contract_type.description = description
        contract_type.save()
        
        messages.success(request, 'Contract type updated successfully')
        return redirect('parcauto_configuration')
        
    except ContractType.DoesNotExist:
        messages.error(request, 'Contract type not found')
        return redirect('parcauto_configuration')
    except Exception as e:
        messages.error(request, f'Error updating contract type: {str(e)}')
        return redirect('parcauto_configuration')

def contract_type_delete(request, type_id):
    """Delete a contract type if not in use"""
    try:
        contract_type = ContractType.objects.get(id=type_id)
        
        if contract_type.contracts.exists():
            messages.error(request, 'Cannot delete - this type is used in existing contracts')
            return redirect('parcauto_configuration')
            
        contract_type.delete()
        messages.success(request, 'Contract type deleted successfully')
        return redirect('parcauto_configuration')
        
    except ContractType.DoesNotExist:
        messages.error(request, 'Contract type not found')
        return redirect('parcauto_configuration')
    except Exception as e:
        messages.error(request, f'Error deleting contract type: {str(e)}')
        return redirect('parcauto_configuration')

# Provider CRUD operations
def provider_create(request):
    """Create a new provider"""
    try:
        name = request.POST.get('provider_name')
        email = request.POST.get('provider_email')
        phone = request.POST.get('provider_phone')
        address = request.POST.get('provider_address')
        
        if not name:
            messages.error(request, 'Provider name is required')
            return redirect('parcauto_configuration')
            
        if Provider.objects.filter(name__iexact=name).exists():
            messages.error(request, 'A provider with this name already exists')
            return redirect('parcauto_configuration')
            
        Provider.objects.create(
            name=name,
            email=email,
            phone=phone,
            address=address
        )
        
        messages.success(request, 'Provider created successfully')
        return redirect('parcauto_configuration')
        
    except Exception as e:
        messages.error(request, f'Error creating provider: {str(e)}')
        return redirect('parcauto_configuration')

def provider_update(request, provider_id):
    """Update an existing provider"""
    try:
        name = request.POST.get('provider_name')
        email = request.POST.get('provider_email')
        phone = request.POST.get('provider_phone')
        address = request.POST.get('provider_address')

        if not name:
            messages.error(request, 'Missing required fields')
            return redirect('parcauto_configuration')

        provider = Provider.objects.get(id=provider_id)
        
        if Provider.objects.filter(name__iexact=name).exclude(id=provider_id).exists():
            messages.error(request, 'This name is already used by another provider')
            return redirect('parcauto_configuration')
            
        provider.name = name
        provider.email = email
        provider.phone = phone
        provider.address = address
        provider.save()
        
        messages.success(request, 'Provider updated successfully')
        return redirect('parcauto_configuration')
        
    except Provider.DoesNotExist:
        messages.error(request, 'Provider not found')
        return redirect('parcauto_configuration')
    except Exception as e:
        messages.error(request, f'Error updating provider: {str(e)}')
        return redirect('parcauto_configuration')

def provider_delete(request, provider_id):
    """Delete a provider if not in use"""
    try:
        provider = Provider.objects.get(id=provider_id)
        
        if provider.contract_set.exists():
            messages.error(request, 'Cannot delete - this provider is used in existing contracts')
            return redirect('parcauto_configuration')
            
        provider.delete()
        messages.success(request, 'Provider deleted successfully')
        return redirect('parcauto_configuration')
        
    except Provider.DoesNotExist:
        messages.error(request, 'Provider not found')
        return redirect('parcauto_configuration')
    except Exception as e:
        messages.error(request, f'Error deleting provider: {str(e)}')
        return redirect('parcauto_configuration')

# Maintenance Type CRUD operations
def entretien_type_create(request):
    """Create a new maintenance type"""
    try:
        nom = request.POST.get('entretien_type_name')
        description = request.POST.get('entretien_type_description', '')
        is_active = request.POST.get('entretien_type_active') == 'on'
        
        if not nom:
            messages.error(request, 'Le nom du type d\'entretien est obligatoire')
            return redirect('parcauto_configuration')
            
        if TypeEntretien.objects.filter(nom__iexact=nom).exists():
            messages.error(request, 'Ce type d\'entretien existe déjà')
            return redirect('parcauto_configuration')
            
        TypeEntretien.objects.create(
            nom=nom,
            description=description,
            is_active=is_active
        )
        
        messages.success(request, f'Type d\'entretien "{nom}" créé avec succès')
        return redirect('parcauto_configuration')
        
    except Exception as e:
        messages.error(request, f'Erreur lors de la création: {str(e)}')
        return redirect('parcauto_configuration')

def entretien_type_update(request, type_id):
    """Update an existing maintenance type"""
    try:
        nom = request.POST.get('entretien_type_name')
        description = request.POST.get('entretien_type_description', '')
        is_active = request.POST.get('entretien_type_active') == 'on'

        if not nom:
            messages.error(request, 'Données manquantes')
            return redirect('parcauto_configuration')

        try:
            entretien_type = TypeEntretien.objects.get(id=type_id)
        except TypeEntretien.DoesNotExist:
            messages.error(request, 'Type d\'entretien introuvable')
            return redirect('parcauto_configuration')
            
        if TypeEntretien.objects.filter(nom__iexact=nom).exclude(id=type_id).exists():
            messages.error(request, 'Un type d\'entretien avec ce nom existe déjà')
            return redirect('parcauto_configuration')
            
        entretien_type.nom = nom
        entretien_type.description = description
        entretien_type.is_active = is_active
        entretien_type.save()
        
        messages.success(request, 'Type d\'entretien mis à jour avec succès')
        return redirect('parcauto_configuration')
        
    except Exception as e:
        messages.error(request, f'Erreur lors de la modification: {str(e)}')
        return redirect('parcauto_configuration')

def entretien_type_delete(request, type_id):
    """Delete a maintenance type if not in use"""
    try:
        try:
            entretien_type = TypeEntretien.objects.get(id=type_id)
            nom = entretien_type.nom
            
            if entretien_type.entretien_set.exists():
                messages.error(request, f'Impossible de supprimer "{nom}" car il est utilisé dans des entretiens')
                return redirect('parcauto_configuration')
                
            entretien_type.delete()
            messages.success(request, f'Type d\'entretien "{nom}" supprimé avec succès')
        except TypeEntretien.DoesNotExist:
            messages.error(request, 'Type d\'entretien introuvable')
            
        return redirect('parcauto_configuration')
        
    except Exception as e:
        messages.error(request, f'Erreur lors de la suppression: {str(e)}')
        return redirect('parcauto_configuration')

# =============================================
# MAINTENANCE (ENTRETIEN) CRUD OPERATIONS
# =============================================

def entretien_list(request):
    """List all maintenance records with pagination"""
    entretiens = Entretien.objects.select_related('vehicle', 'type_entretien').order_by('-date_planifiee')
    vehicules = Vehicule.objects.all()
    types_entretien = TypeEntretien.objects.filter(is_active=True)
    
    # Pagination
    items_per_page = request.GET.get('items_per_page', 5)
    paginator = Paginator(entretiens, items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'entretiens': page_obj,
        'vehicules': vehicules,
        'types_entretien': types_entretien,
        'statuts_entretien': Entretien._meta.get_field('StatutEntretien').choices,
        'today': timezone.now().date(),
    }
    return render(request, 'entretien.html', context)

def entretien_create(request):
    """Create a new maintenance record"""
    try:
        vehicule_id = request.POST.get('vehicule')
        type_entretien_id = request.POST.get('type_entretien')
        date_planifiee = request.POST.get('date_planifiee')
        statut = request.POST.get('statut')
        remarque = request.POST.get('remarque', '')
        piece_jointe = request.FILES.get('piece_jointe')

        if not all([vehicule_id, type_entretien_id, date_planifiee, statut]):
            messages.error(request, 'Tous les champs obligatoires doivent être remplis.')
            return redirect('entretien')

        vehicule = Vehicule.objects.get(id=vehicule_id)
        type_entretien = TypeEntretien.objects.get(id=type_entretien_id)

        Entretien.objects.create(
            vehicle=vehicule,
            type_entretien=type_entretien,
            date_planifiee=date_planifiee,
            StatutEntretien=statut,
            remarque=remarque,
            piece_jointe=piece_jointe
        )

        messages.success(request, "Entretien ajouté avec succès.")
        return redirect('entretien')

    except Exception as e:
        messages.error(request, f"Erreur lors de l'ajout de l'entretien : {str(e)}")
        return redirect('entretien')

def entretien_update(request):
    """Update an existing maintenance record"""
    try:
        entretien_id = request.POST.get('entretien_id')
        vehicule_id = request.POST.get('vehicule')
        type_entretien_id = request.POST.get('type_entretien')
        date_planifiee = request.POST.get('date_planifiee')
        statut = request.POST.get('statut')
        remarque = request.POST.get('remarque', '')
        piece_jointe = request.FILES.get('piece_jointe')

        if not all([entretien_id, vehicule_id, type_entretien_id, date_planifiee, statut]):
            messages.error(request, 'Données manquantes pour la modification.')
            return redirect('entretien')

        entretien = Entretien.objects.get(id=entretien_id)
        vehicule = Vehicule.objects.get(id=vehicule_id)
        type_entretien = TypeEntretien.objects.get(id=type_entretien_id)

        entretien.vehicle = vehicule
        entretien.type_entretien = type_entretien
        entretien.date_planifiee = date_planifiee
        entretien.StatutEntretien = statut
        entretien.remarque = remarque
        if piece_jointe:
            entretien.piece_jointe = piece_jointe
        entretien.save()

        messages.success(request, "Entretien modifié avec succès.")
        return redirect('entretien')

    except Exception as e:
        messages.error(request, f"Erreur lors de la modification : {str(e)}")
        return redirect('entretien')

def entretien_delete(request):
    """Delete a maintenance record"""
    try:
        entretien_id = request.POST.get('entretien_id')
        if not entretien_id:
            messages.error(request, "ID d'entretien manquant.")
            return redirect('entretien')

        entretien = Entretien.objects.get(id=entretien_id)
        entretien.delete()

        messages.success(request, "Entretien supprimé avec succès.")
        return redirect('entretien')

    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
        return redirect('entretien')

def entretien_events(request):
    """Get maintenance events for calendar view"""
    entretiens = Entretien.objects.select_related('vehicle', 'type_entretien').all()
    events = []
    
    for entretien in entretiens:
        event = {
            'id': entretien.id,
            'title': f"{entretien.vehicle.immatriculation} - {entretien.type_entretien.nom}",
            'start': entretien.date_planifiee.isoformat(),
            'className': '',
            'extendedProps': {
                'type': entretien.type_entretien.nom,
                'status': entretien.statut,
                'remarque': entretien.remarque or '',
                'vehicule': entretien.vehicle.immatriculation
            }
        }
        
        # Set color based on status
        if entretien.statut == Entretien.StatutEntretien.PLANIFIE:
            event['className'] = 'bg-planned'
        elif entretien.statut == Entretien.StatutEntretien.EFFECTUE:
            event['className'] = 'bg-completed'
        elif entretien.statut == Entretien.StatutEntretien.EN_RETARD:
            event['className'] = 'bg-late'
        
        events.append(event)
    
    return JsonResponse(events, safe=False)

# =============================================
# VEHICLE ASSIGNMENT (AFFECTATION) CRUD OPERATIONS
# =============================================

@gzip_page
@require_http_methods(["GET", "POST"])
def affectation(request):
    """Main assignment view with action routing"""
    try:
        if request.method == 'POST':
            print("Received POST data:", request.POST)
            action = request.POST.get('action')
            affectation_id = request.POST.get('affectation_id')

            if not action:
                messages.error(request, 'Action non spécifiée')
                return redirect('affectation')

            if action in ['edit', 'terminate', 'delete'] and not affectation_id:
                messages.error(request, 'ID d\'affectation manquant')
                return redirect('affectation')

            try:
                if action == 'add':
                    return affectation_create(request)
                elif action == 'edit':
                    affectation = Affectation.objects.get(id=affectation_id)
                    return affectation_edit(request, affectation)
                elif action == 'terminate':
                    affectation = Affectation.objects.get(id=affectation_id)
                    return affectation_terminate(request, affectation)
                elif action == 'delete':
                    affectation = Affectation.objects.get(id=affectation_id)
                    return affectation_delete(request, affectation)
            except Affectation.DoesNotExist:
                messages.error(request, 'Affectation introuvable')
                return redirect('affectation')
            except Exception as e:
                logger.error(f"Error processing affectation action {action}: {str(e)}", exc_info=True)
                messages.error(request, f'Erreur: {str(e)}')
                return redirect('affectation')

        # GET request handling with optimized query and pagination
        query = request.GET.get('q', '').strip()
        statut = request.GET.get('statut')
        page_number = request.GET.get('page')

        # Base queryset with select_related and only for optimization
        affectations_qs = Affectation.objects.select_related(
            'vehicle', 
            'driver'
        ).only(
            'id',
            'date_debut',
            'date_fin',
            'kilometrage_debut',
            'kilometrage_fin',
            'statut',
            'vehicle__immatriculation',
            'vehicle__id',
            'driver__full_name',
            'driver__id'
        ).order_by('-date_debut')

        # Apply filters if provided
        if query:
            affectations_qs = affectations_qs.filter(
                Q(vehicle__immatriculation__icontains=query) |
                Q(driver__full_name__icontains=query)
            )
        
        if statut:
            affectations_qs = affectations_qs.filter(statut=statut)

        # Pagination - 10 items per page
        paginator = Paginator(affectations_qs, 5)
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
            'vehicules': Vehicule.objects.only('id', 'immatriculation', 'marque__nom', 'modele__nom'),
            'vehicules_disponibles': Vehicule.objects.filter(statut='disponible').only('id', 'immatriculation'),
            'employees': Employee.objects.filter(status='A').only('id', 'full_name', 'employee_id').order_by('full_name'),
            'today': timezone.now().date(),
            'query': query,
            'statut': statut,
        }

        return render(request, 'affectation.html', context)

    except Exception as e:
        logger.error(f"Error in affectation view: {str(e)}", exc_info=True)
        messages.error(request, 'Une erreur technique est survenue')
        return redirect('parcauto_home')

def affectation_create(request):
    """Create a new vehicle assignment"""
    try:
        vehicle_id = request.POST.get('vehicle_id')
        driver_id = request.POST.get('driver_id')
        date_debut = request.POST.get('date_debut')
        kilometrage_debut = int(request.POST.get('kilometrage_debut', 0))
        
        if not all([vehicle_id, driver_id, date_debut]):
            messages.error(request, 'Tous les champs sont obligatoires')
            return redirect('affectation')
            
        vehicle = Vehicule.objects.get(id=vehicle_id)
        driver = Employee.objects.get(id=driver_id)
        
        affectation = Affectation.objects.create(
            vehicle=vehicle,
            driver=driver,
            date_debut=date_debut,
            kilometrage_debut=kilometrage_debut,
            statut='A'
        )
        
        vehicle.statut = StatutVehicule.EN_SERVICE
        vehicle.kilometrage_actuel = kilometrage_debut
        vehicle.save()
        
        messages.success(request, 'Affectation créée avec succès')
        
    except Vehicule.DoesNotExist:
        messages.error(request, 'Véhicule introuvable')
    except Employee.DoesNotExist:
        messages.error(request, 'Conducteur introuvable')
    except Exception as e:
        messages.error(request, f'Erreur: {str(e)}')
    
    return redirect('affectation')

def affectation_edit(request, affectation):
    """Update an existing vehicle assignment"""
    try:
        vehicle_id = request.POST.get('vehicle_id')
        driver_id = request.POST.get('driver_id')
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin', None)
        kilometrage_debut = int(request.POST.get('kilometrage_debut', 0))
        kilometrage_fin = int(request.POST.get('kilometrage_fin', 0)) if request.POST.get('kilometrage_fin') else None
        statut = request.POST.get('statut')
        
        affectation.vehicle_id = vehicle_id
        affectation.driver_id = driver_id
        affectation.date_debut = date_debut
        affectation.date_fin = date_fin
        affectation.kilometrage_debut = kilometrage_debut
        affectation.kilometrage_fin = kilometrage_fin
        affectation.statut = statut
        
        affectation.save()
        
        if statut == 'T':
            vehicle = affectation.vehicle
            vehicle.kilometrage_actuel = kilometrage_fin
            vehicle.save()
            
            has_active = Affectation.objects.filter(
                vehicle=vehicle, 
                statut='A'
            ).exists()
            if not has_active:
                vehicle.statut = StatutVehicule.DISPONIBLE
                vehicle.save()
        
        messages.success(request, 'Affectation mise à jour avec succès')
        
    except Exception as e:
        messages.error(request, f'Erreur lors de la modification: {str(e)}')
    
    return redirect('affectation')

def affectation_terminate(request, affectation):
    """Terminate an active vehicle assignment"""
    try:
        kilometrage_fin = int(request.POST.get('kilometrage_fin', 0))
        date_fin_str = request.POST.get('date_fin')
        
        # Convert string date to proper date object
        if date_fin_str:
            try:
                date_fin = datetime.strptime(date_fin_str, '%Y-%m-%d').date()
            except ValueError:
                try:
                    date_fin = datetime.strptime(date_fin_str, '%d/%m/%Y').date()
                except ValueError:
                    messages.error(request, 'Format de date invalide')
                    return redirect('affectation')
        else:
            date_fin = timezone.now().date()
        
        affectation.kilometrage_fin = kilometrage_fin
        affectation.date_fin = date_fin
        affectation.statut = 'T'
        affectation.save()
        
        vehicle = affectation.vehicle
        vehicle.kilometrage_actuel = kilometrage_fin
        vehicle.statut = StatutVehicule.DISPONIBLE
        vehicle.save()
        
        messages.success(request, 'Affectation terminée avec succès')
        
    except Exception as e:
        messages.error(request, f'Erreur: {str(e)}')
    
    return redirect('affectation')

def affectation_delete(request, affectation):
    """Delete a vehicle assignment"""
    try:
        vehicle = affectation.vehicle
        
        if affectation.statut == 'A':
            vehicle.statut = StatutVehicule.DISPONIBLE
            vehicle.save()
        
        affectation.delete()
        
        messages.success(request, 'Affectation supprimée avec succès')
        
    except Exception as e:
        messages.error(request, f'Erreur: {str(e)}')
    
    return redirect('affectation')

# =============================================
# CONTRACT MANAGEMENT CRUD OPERATIONS
# =============================================

def contract_list(request):
    """List all contracts with filtering and pagination"""
    try:
        contracts = Contract.objects.select_related(
            'vehicle', 
            'contract_type', 
            'provider'
        ).order_by('-start_date')

        # Filtering
        search_query = request.GET.get('search')
        type_filter = request.GET.get('type')
        status_filter = request.GET.get('status')

        if search_query:
            contracts = contracts.filter(
                Q(vehicle__immatriculation__icontains=search_query) |
                Q(contract_type__name__icontains=search_query) |
                Q(provider__name__icontains=search_query) |
                Q(reference_number__icontains=search_query)
            )

        if type_filter:
            contracts = contracts.filter(contract_type__id=type_filter)

        if status_filter == 'active':
            contracts = contracts.filter(is_active=True)
        elif status_filter == 'expired':
            contracts = contracts.filter(is_expired=True)

        # Pagination
        paginator = Paginator(contracts, 10)
        page_number = request.GET.get('page')

        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        context = {
            'page_obj': page_obj,
            'contract_types': ContractType.objects.all(),
            'providers': Provider.objects.all(),
            'vehicules': Vehicule.objects.all(),
            'today': timezone.now().date(),
        }

        return render(request, 'contract.html', context)

    except Exception as e:
        logger.error(f"Error in contract list view: {str(e)}", exc_info=True)
        messages.error(request, 'Une erreur technique est survenue')
        return redirect('parcauto_home')

def contract_create(request):
    """Create a new contract"""
    try:
        vehicle_id = request.POST.get('vehicle_id')
        contract_type_id = request.POST.get('contract_type_id')
        provider_id = request.POST.get('provider_id')
        reference_number = request.POST.get('reference_number')
        start_date = request.POST.get('start_date')
        expiration_date = request.POST.get('expiration_date')
        contract_file = request.FILES.get('contract_file')
        notes = request.POST.get('notes', '')
        
        if not all([vehicle_id, contract_type_id, provider_id, start_date, expiration_date, contract_file]):
            messages.error(request, 'Veuillez remplir tous les champs obligatoires')
            return redirect('contract')
            
        try:
            vehicle = Vehicule.objects.get(id=vehicle_id)
            contract_type = ContractType.objects.get(id=contract_type_id)
            provider = Provider.objects.get(id=provider_id)
        except (Vehicule.DoesNotExist, ContractType.DoesNotExist, Provider.DoesNotExist) as e:
            messages.error(request, 'Données invalides: ' + str(e))
            return redirect('contract')
            
        # Validate dates
        start_date_obj = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
        expiration_date_obj = timezone.datetime.strptime(expiration_date, '%Y-%m-%d').date()
        
        if expiration_date_obj < start_date_obj:
            messages.error(request, 'La date d\'expiration doit être postérieure à la date de début')
            return redirect('contract')
            
        Contract.objects.create(
            vehicle=vehicle,
            contract_type=contract_type,
            provider=provider,
            reference_number=reference_number,
            start_date=start_date,
            expiration_date=expiration_date,
            contract_file=contract_file,
            notes=notes,
            is_active=True
        )
        
        messages.success(request, 'Contrat créé avec succès')
        return redirect('contract')
        
    except Exception as e:
        logger.error(f"Error creating contract: {str(e)}", exc_info=True)
        messages.error(request, f'Erreur lors de la création du contrat: {str(e)}')
        return redirect('contract')

def contract_update(request):
    """Update an existing contract"""
    try:
        contract_id = request.POST.get('contract_id')
        vehicle_id = request.POST.get('vehicle_id')
        contract_type_id = request.POST.get('contract_type_id')
        provider_id = request.POST.get('provider_id')
        reference_number = request.POST.get('reference_number')
        start_date = request.POST.get('start_date')
        expiration_date = request.POST.get('expiration_date')
        contract_file = request.FILES.get('contract_file')
        notes = request.POST.get('notes', '')
        is_active = request.POST.get('is_active') == '1'
        
        if not all([contract_id, vehicle_id, contract_type_id, provider_id, start_date, expiration_date]):
            messages.error(request, 'Veuillez remplir tous les champs obligatoires')
            return redirect('contract')
            
        try:
            contract = Contract.objects.get(id=contract_id)
            vehicle = Vehicule.objects.get(id=vehicle_id)
            contract_type = ContractType.objects.get(id=contract_type_id)
            provider = Provider.objects.get(id=provider_id)
        except (Contract.DoesNotExist, Vehicule.DoesNotExist, 
               ContractType.DoesNotExist, Provider.DoesNotExist) as e:
            messages.error(request, 'Données invalides: ' + str(e))
            return redirect('contract')
            
        # Validate dates
        start_date_obj = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
        expiration_date_obj = timezone.datetime.strptime(expiration_date, '%Y-%m-%d').date()
        
        if expiration_date_obj < start_date_obj:
            messages.error(request, 'La date d\'expiration doit être postérieure à la date de début')
            return redirect('contract')
            
        contract.vehicle = vehicle
        contract.contract_type = contract_type
        contract.provider = provider
        contract.reference_number = reference_number
        contract.start_date = start_date
        contract.expiration_date = expiration_date
        contract.notes = notes
        contract.is_active = is_active
        
        if contract_file:
            contract.contract_file = contract_file
            
        contract.save()
        
        messages.success(request, 'Contrat mis à jour avec succès')
        return redirect('contract')
        
    except Exception as e:
        logger.error(f"Error updating contract: {str(e)}", exc_info=True)
        messages.error(request, f'Erreur lors de la modification du contrat: {str(e)}')
        return redirect('contract')

def contract_delete(request):
    """Delete a contract"""
    try:
        contract_id = request.POST.get('contract_id')
        if not contract_id:
            messages.error(request, 'ID de contrat manquant')
            return redirect('contract')
            
        contract = Contract.objects.get(id=contract_id)
        contract.delete()
        
        messages.success(request, 'Contrat supprimé avec succès')
        return redirect('contract')
        
    except Contract.DoesNotExist:
        messages.error(request, 'Contrat introuvable')
        return redirect('contract')
    except Exception as e:
        logger.error(f"Error deleting contract: {str(e)}", exc_info=True)
        messages.error(request, f'Erreur lors de la suppression du contrat: {str(e)}')
        return redirect('contract')

# =============================================
# MAIN VIEW ROUTERS
# =============================================

def contract(request):
    """Route contract requests to appropriate handler"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            return contract_create(request)
        elif action == 'edit':
            return contract_update(request)
        elif action == 'delete':
            return contract_delete(request)
    
    return contract_list(request)

def parcauto_home(request):
    """Route vehicle management requests to appropriate handler"""
    if request.method == 'POST':
        action = request.POST.get('action', 'add')
        
        if action == 'add':
            return parcauto_create(request)
        elif action == 'edit':
            return parcauto_update(request)
        elif action == 'delete':
            return parcauto_delete(request)
    
    return parcauto_list(request)

def configuration(request):
    """Route configuration requests to appropriate handler"""
    if request.method == 'POST':
        action = request.POST.get('action', 'add')
        
        if action == 'add_marque':
            return marque_create(request)
        elif action == 'edit_marque':
            return marque_update(request)
        elif action == 'delete_marque':
            return marque_delete(request)
        elif action == 'add_modele':
            return modele_create(request)
        elif action == 'edit_modele':
            return modele_update(request)
        elif action == 'delete_modele':
            return modele_delete(request)
        elif action == 'add_entretien_type':
            return entretien_type_create(request)
        elif action == 'edit_entretien_type':
            return entretien_type_update(request)
        elif action == 'delete_entretien_type':
            return entretien_type_delete(request)
        elif action == 'add_contract_type':
            return contract_type_create(request)
        elif action == 'edit_contract_type':
            return contract_type_update(request)
        elif action == 'delete_contract_type':
            return contract_type_delete(request)
        elif action == 'add_provider':
            return provider_create(request)
        elif action == 'edit_provider':
            return provider_update(request)
        elif action == 'delete_provider':
            return provider_delete(request)
    
    return configuration_list(request)

def entretien(request):
    """Route maintenance requests to appropriate handler"""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_entretien':
            return entretien_create(request)
        elif action == 'edit_entretien':
            return entretien_update(request)
        elif action == 'delete_entretien':
            return entretien_delete(request)

    return entretien_list(request)

# =============================================
# UTILITY FUNCTIONS AND AJAX ENDPOINTS
# =============================================

@require_GET
def get_modeles_by_marque(request, marque_id):
    """AJAX endpoint to get models by brand"""
    try:
        if not marque_id or not str(marque_id).isdigit():
            return JsonResponse({'error': 'Invalid marque ID'}, status=400)
            
        modeles = Modele.objects.filter(marque_id=marque_id).order_by('nom')
        
        if not modeles.exists():
            return JsonResponse([], safe=False)
        
        data = [{'id': modele.id, 'nom': modele.nom} for modele in modeles]
        return JsonResponse(data, safe=False)
        
    except Exception as e:
        logger.error(f"Error in get_modeles_by_marque: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Server error'}, status=500)

@require_GET
def get_expiring_contracts_count(request):
    """AJAX endpoint to count contracts expiring soon"""
    try:
        today = timezone.now().date()
        soon_threshold = today + timedelta(days=30)

        candidates = Contract.objects.filter(
            expiration_date__gte=today,
            expiration_date__lte=soon_threshold,
            is_active=True
        )

        count = candidates.count()

        return JsonResponse({
            'status': 'success',
            'count': count,
            'debug': {
                'today': today.isoformat(),
                'threshold': soon_threshold.isoformat(),
                'total_active_contracts': Contract.objects.filter(is_active=True).count(),
                'example_dates': [
                    str(c.expiration_date) for c in Contract.objects.filter(is_active=True)[:5]
                ] if Contract.objects.filter(is_active=True).exists() else []
            }
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e), 'count': 0}, status=500)

# =============================================
# STATISTICS AND REPORTING FUNCTIONS
# =============================================

def statistics(request):
    """Main statistics dashboard view"""
    try:
        # General statistics
        total_vehicles = Vehicule.objects.count()
        average_kilometers = Vehicule.objects.aggregate(avg=Avg('kilometrage_actuel'))['avg'] or 0
        current_year = timezone.now().year
        average_vehicle_age = Vehicule.objects.aggregate(
            avg_age=Avg(current_year - F('annee'))
        )['avg_age'] or 0
        active_assignments = Affectation.objects.filter(statut='A').count()
        maintenance_this_month = Entretien.objects.filter(
            date_planifiee__month=timezone.now().month,
            date_planifiee__year=timezone.now().year
        ).count()
        
        # Vehicle status statistics
        vehicle_status = Vehicule.objects.values('statut').annotate(count=Count('id'))
        status_choices = dict(StatutVehicule.choices)
        vehicle_status_labels = [status_choices.get(item['statut'], item['statut']) for item in vehicle_status]
        vehicle_status_data = [item['count'] for item in vehicle_status]

        # Vehicle type statistics
        vehicle_type = Vehicule.objects.values('type').annotate(count=Count('id'))
        type_choices = dict(TypeVehicule.choices)
        vehicle_type_labels = [type_choices.get(item['type'], item['type']) for item in vehicle_type]
        vehicle_type_data = [item['count'] for item in vehicle_type]

        # Get all models for filter dropdown
        models = Modele.objects.select_related('marque').all()

        # Default model statistics - Initialize with empty data
        model_stats = {
            'marque': 'N/A',
            'nom': 'Select a model',
            'vehicle_count': 0,
            'average_kilometers': 0,
            'max_kilometers': 0,
            'min_kilometers': 0,
            'total_kilometers': 0,
            'average_year': 0,
            'average_age': 0,
            'first_purchase': None,
            'last_purchase': None,
            'maintenance_by_type': [],
            'total_assignments': 0,
            'active_assignments': 0,
            'avg_assignment_duration': 0,
            'avg_assignment_kilometers': 0,
            'unique_drivers': 0,
        }
        
        model_charts_data = {
            'model_status_labels': [],
            'model_status_data': [],
            'maintenance_type_labels': [],
            'maintenance_type_data': [],
            'maintenance_status_labels': [],
            'maintenance_status_data': [],
            'assignment_labels': ['Active', 'Terminated'],
            'assignment_data': [0, 0],
            'assignment_history_labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'assignment_history_data': [0] * 12,
        }

        context = {
            'total_vehicles': total_vehicles,
            'average_kilometers': average_kilometers,
            'average_vehicle_age': average_vehicle_age,
            'active_assignments': active_assignments,
            'maintenance_this_month': maintenance_this_month,
            'vehicle_status_labels': json.dumps(vehicle_status_labels),
            'vehicle_status_data': json.dumps(vehicle_status_data),
            'vehicle_type_labels': json.dumps(vehicle_type_labels),
            'vehicle_type_data': json.dumps(vehicle_type_data),
            'models': models,
            'model_stats': model_stats,
            'model_charts_data': json.dumps(model_charts_data),
        }
        return render(request, 'parcauto_statistics.html', context)
        
    except Exception as e:
        logger.error(f"Error in statistics view: {str(e)}")
        logger.error(traceback.format_exc())
        context = {
            'total_vehicles': 0,
            'average_kilometers': 0,
            'average_vehicle_age': 0,
            'active_assignments': 0,
            'maintenance_this_month': 0,
            'vehicle_status_labels': json.dumps([]),
            'vehicle_status_data': json.dumps([]),
            'vehicle_type_labels': json.dumps([]),
            'vehicle_type_data': json.dumps([]),
            'models': Modele.objects.none(),
            'model_stats': {'error': str(e)},
            'model_charts_data': json.dumps({}),
        }
        return render(request, 'parcauto_statistics.html', context)

def get_model_statistics(model_id):
    """Get statistics for specific vehicle model"""
    try:
        logger.info(f"Getting statistics for model ID: {model_id}")
        
        if not Modele.objects.filter(id=model_id).exists():
            raise ValueError(f"Model with id {model_id} does not exist")
        
        model = Modele.objects.select_related('marque').get(id=model_id)
        vehicles = Vehicule.objects.filter(modele_id=model_id)
        vehicle_count = vehicles.count()
        
        logger.info(f"Found {vehicle_count} vehicles for model {model.nom}")
        
        stats = {
            'marque': model.marque.nom if model.marque else 'N/A',
            'nom': model.nom,
            'vehicle_count': vehicle_count,
        }
        
        if vehicle_count == 0:
            stats.update({
                'average_kilometers': 0,
                'max_kilometers': 0,
                'min_kilometers': 0,
                'total_kilometers': 0,
                'average_year': 0,
                'average_age': 0,
                'first_purchase': None,
                'last_purchase': None,
                'maintenance_by_type': [],
                'total_assignments': 0,
                'active_assignments': 0,
                'avg_assignment_duration': 0,
                'avg_assignment_kilometers': 0,
                'unique_drivers': 0,
            })
            return stats
        
        # Kilometer statistics
        try:
            km_stats = vehicles.aggregate(
                avg=Avg('kilometrage_actuel'),
                max=Max('kilometrage_actuel'),
                min=Min('kilometrage_actuel'),
                total=Sum('kilometrage_actuel')
            )
            stats.update({
                'average_kilometers': km_stats['avg'] or 0,
                'max_kilometers': km_stats['max'] or 0,
                'min_kilometers': km_stats['min'] or 0,
                'total_kilometers': km_stats['total'] or 0,
            })
        except Exception as e:
            logger.error(f"Error calculating kilometer stats: {str(e)}")
            stats.update({
                'average_kilometers': 0,
                'max_kilometers': 0,
                'min_kilometers': 0,
                'total_kilometers': 0,
            })
        
        # Year statistics
        try:
            year_stats = vehicles.aggregate(
                avg_year=Avg('annee'),
                first_purchase=Min('date_achat'),
                last_purchase=Max('date_achat')
            )
            current_year = timezone.now().year
            avg_year = year_stats['avg_year'] or current_year
            stats.update({
                'average_year': round(avg_year),
                'average_age': current_year - avg_year,
                'first_purchase': year_stats['first_purchase'],
                'last_purchase': year_stats['last_purchase'],
            })
        except Exception as e:
            logger.error(f"Error calculating year stats: {str(e)}")
            current_year = timezone.now().year
            stats.update({
                'average_year': current_year,
                'average_age': 0,
                'first_purchase': None,
                'last_purchase': None,
            })
        
        # Maintenance statistics
        try:
            maintenance = Entretien.objects.filter(vehicle__modele_id=model_id)
            maintenance_by_type = list(maintenance.values('type_entretien__nom').annotate(
                total=Count('id'),
                planned=Count('id', filter=Q(StatutEntretien='planifié')),
                completed=Count('id', filter=Q(StatutEntretien='effectué')),
                overdue=Count('id', filter=Q(StatutEntretien='en_retard'))
            ))
            stats['maintenance_by_type'] = maintenance_by_type
        except Exception as e:
            logger.error(f"Error calculating maintenance stats: {str(e)}")
            stats['maintenance_by_type'] = []
        
        # Assignment statistics
        try:
            assignments = Affectation.objects.filter(vehicle__modele_id=model_id)
            assignment_stats = assignments.aggregate(
                total=Count('id'),
                active=Count('id', filter=Q(statut='A')),
                avg_km=Avg('distance_parcourue')
            )
            
            avg_duration_days = 0
            try:
                finished_assignments = assignments.filter(date_fin__isnull=False)
                if finished_assignments.exists():
                    durations = []
                    for assignment in finished_assignments:
                        if assignment.date_debut and assignment.date_fin:
                            duration = (assignment.date_fin - assignment.date_debut).days
                            durations.append(duration)
                    if durations:
                        avg_duration_days = sum(durations) / len(durations)
            except Exception as e:
                logger.error(f"Error calculating assignment duration: {str(e)}")
            
            stats.update({
                'total_assignments': assignment_stats['total'] or 0,
                'active_assignments': assignment_stats['active'] or 0,
                'avg_assignment_duration': avg_duration_days,
                'avg_assignment_kilometers': assignment_stats['avg_km'] or 0,
                'unique_drivers': assignments.values('driver').distinct().count(),
            })
        except Exception as e:
            logger.error(f"Error calculating assignment stats: {str(e)}")
            stats.update({
                'total_assignments': 0,
                'active_assignments': 0,
                'avg_assignment_duration': 0,
                'avg_assignment_kilometers': 0,
                'unique_drivers': 0,
            })
        
        logger.info(f"Successfully calculated stats for model {model_id}")
        return stats
        
    except Exception as e:
        logger.error(f"Error getting model statistics: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def get_model_charts_data(model_id):
    """Get chart data for specific vehicle model"""
    try:
        logger.info(f"Getting chart data for model ID: {model_id}")
        
        vehicles = Vehicule.objects.filter(modele_id=model_id)
        
        charts_data = {
            'model_status_labels': [],
            'model_status_data': [],
            'maintenance_type_labels': [],
            'maintenance_type_data': [],
            'maintenance_status_labels': [],
            'maintenance_status_data': [],
            'assignment_labels': ['Active', 'Terminated'],
            'assignment_data': [0, 0],
            'assignment_history_labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'assignment_history_data': [0] * 12,
        }
        
        # Status distribution
        try:
            status_data = vehicles.values('statut').annotate(count=Count('id'))
            try:
                status_choices = dict(StatutVehicule.choices)
            except:
                status_choices = {}
            
            for item in status_data:
                status_label = status_choices.get(item['statut'], str(item['statut']))
                charts_data['model_status_labels'].append(status_label)
                charts_data['model_status_data'].append(item['count'])
        except Exception as e:
            logger.error(f"Error getting status data: {str(e)}")
        
        # Maintenance data
        try:
            maintenance = Entretien.objects.filter(vehicle__modele_id=model_id)
            
            maintenance_types = maintenance.values('type_entretien__nom').annotate(
                count=Count('id')
            ).order_by('-count')[:5]
            
            for item in maintenance_types:
                type_name = item['type_entretien__nom'] or 'N/A'
                charts_data['maintenance_type_labels'].append(type_name)
                charts_data['maintenance_type_data'].append(item['count'])
            
            status_map = {'planifié': 'Planned', 'effectué': 'Completed', 'en_retard': 'Overdue'}
            maintenance_status = maintenance.values('StatutEntretien').annotate(count=Count('id'))
            for item in maintenance_status:
                status_label = status_map.get(item['StatutEntretien'], str(item['StatutEntretien']))
                charts_data['maintenance_status_labels'].append(status_label)
                charts_data['maintenance_status_data'].append(item['count'])
        except Exception as e:
            logger.error(f"Error getting maintenance data: {str(e)}")
        
        # Assignment data
        try:
            assignments = Affectation.objects.filter(vehicle__modele_id=model_id)
            active_count = assignments.filter(statut='A').count()
            terminated_count = assignments.filter(statut='T').count()
            charts_data['assignment_data'] = [active_count, terminated_count]
            
            assignment_history = assignments.annotate(
                month=ExtractMonth('date_debut')
            ).values('month').annotate(count=Count('id'))
            
            for item in assignment_history:
                month_index = item['month'] - 1
                if 0 <= month_index < 12:
                    charts_data['assignment_history_data'][month_index] = item['count']
        except Exception as e:
            logger.error(f"Error getting assignment data: {str(e)}")
        
        logger.info(f"Successfully got chart data for model {model_id}")
        return charts_data
        
    except Exception as e:
        logger.error(f"Error getting chart data for model {model_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            'model_status_labels': [],
            'model_status_data': [],
            'maintenance_type_labels': [],
            'maintenance_type_data': [],
            'maintenance_status_labels': [],
            'maintenance_status_data': [],
            'assignment_labels': ['Active', 'Terminated'],
            'assignment_data': [0, 0],
            'assignment_history_labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'assignment_history_data': [0] * 12,
        }

@csrf_exempt
def get_model_data_ajax(request, model_id):
    """AJAX endpoint for model data"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        logger.info(f"AJAX request for model data: {model_id}")
        
        try:
            model_id = int(model_id)
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'Invalid model ID'}, status=400)
        
        if not Modele.objects.filter(id=model_id).exists():
            return JsonResponse({'success': False, 'error': 'Model not found'}, status=404)
        
        model_stats = get_model_statistics(model_id)
        charts_data = get_model_charts_data(model_id)
        
        response_data = {
            'success': True,
            'model_stats': model_stats,
            'charts_data': charts_data
        }
        
        logger.info(f"Successfully returning data for model {model_id}")
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Unexpected error in get_model_data_ajax: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({
            'success': False,  
            'error': f'Internal server error: {str(e)}'
        }, status=500)