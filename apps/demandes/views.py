from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.template.loader import render_to_string
from django.db import transaction
from django.db.models import Count, Q, F
from django.views.decorators.http import require_POST
from django.http import JsonResponse

import logging
from django.utils import timezone

from .models import Priorite, Statut, Produit, DemandeInterne, DemandeProduit,DemandePatient,DemandePatientModel
from apps.hr.models import Department
from apps.purchases.models import Supplier

logger = logging.getLogger(__name__)


def paginate(queryset, page_key, per_page_key, request, default_per_page=5):
    per_page = int(request.GET.get(per_page_key, default_per_page))
    page = request.GET.get(page_key, 1)
    paginator = Paginator(queryset, per_page)
    try:
        return paginator.page(page)
    except:
        return paginator.page(1)


def redirect_with_tab(request, default_tab='produits'):
    """Redirige vers la configuration en conservant l'onglet actif"""
    active_tab = getattr(request, 'active_tab', None) or request.POST.get('active_tab', default_tab)
    from django.urls import reverse
    url = reverse('demandes:configuration_demandes')
    return redirect(f'{url}?active_tab={active_tab}')


def configuration_list(request, active_tab=None):
    if active_tab is None:
        active_tab = request.GET.get('active_tab', 'produits')
    priorites_page = paginate(
        Priorite.objects.all().order_by('niveau'), 
        'page_priorites', 'priorites_per_page', request
    )
    statuts_page = paginate(
        Statut.objects.all().order_by('nom'), 
        'page_statuts', 'statuts_per_page', request
    )
    produits_page = paginate(
        Produit.objects.all().order_by('nom'),
        'page_produits', 'produits_per_page', request
    )
    patients_page = paginate(
        DemandePatientModel.objects.all().order_by('nom', 'prenom'),
        'page_patients', 'patients_per_page', request
    )
    
    # Ajouter la pagination des départements
    departements_page = paginate(
        Department.objects.all().order_by('name'),
        'page_departements', 'departements_per_page', request
    )
    
    # Ajouter la pagination des prestataires
    prestataires_page = paginate(
        Supplier.objects.all().order_by('name'),
        'page_prestataires', 'prestataires_per_page', request
    )
    
    context = {
        'priorites_page': priorites_page,
        'statuts_page': statuts_page,
        'produits_page': produits_page,
        'patients_page': patients_page,
        'departements_page': departements_page,
        'prestataires_page': prestataires_page,  # Ajouter les prestataires au contexte
        'active_tab': active_tab,
    }
    return render(request, 'configuration_demandes.html', context)
# =============================================
# PRODUIT - CRUD
# =============================================
@require_POST
def produit_create(request):
    nom = request.POST.get('nom')
    description = request.POST.get('description', '')
    type_demande = request.POST.get('type_demande')
    image = request.FILES.get('image')
    disponible = 'disponible' in request.POST
    if not all([nom, type_demande]):
        messages.error(request, 'Nom et type sont obligatoires.')
        return redirect_with_tab(request, 'produits')
    try:
        Produit.objects.create(
            nom=nom,
            description=description,
            type_demande=type_demande,
            image=image,
            disponible=disponible
        )
        messages.success(request, f'Produit "{nom}" ajouté.')
    except Exception as e:
        logger.error(f"Erreur création produit: {str(e)}")
        messages.error(request, 'Erreur technique.')
    return redirect_with_tab(request, 'produits')


@require_POST
def produit_update(request):
    produit_id = request.POST.get('produit_id')
    nom = request.POST.get('nom')
    description = request.POST.get('description', '')
    type_demande = request.POST.get('type_demande')
    image = request.FILES.get('image')
    disponible = 'disponible' in request.POST
    if not all([produit_id, nom, type_demande]):
        messages.error(request, 'Données manquantes.')
        return redirect_with_tab(request, 'produits')
    try:
        produit = get_object_or_404(Produit, id=produit_id)
        produit.nom = nom
        produit.description = description
        produit.type_demande = type_demande
        produit.disponible = disponible
        if image:
            produit.image = image
        produit.save()
        messages.success(request, 'Produit mis à jour.')
    except Exception as e:
        logger.error(f"Erreur modification produit: {str(e)}")
        messages.error(request, 'Erreur technique.')
    return redirect_with_tab(request, 'produits')


@require_POST
def produit_delete(request):
    produit_id = request.POST.get('produit_id')
    if not produit_id:
        messages.error(request, 'ID produit manquant.')
        return redirect_with_tab(request, 'produits')
    try:
        produit = get_object_or_404(Produit, id=produit_id)
        produit.delete()
        messages.success(request, 'Produit supprimé.')
    except Exception as e:
        logger.error(f"Erreur suppression produit: {str(e)}")
        messages.error(request, 'Erreur technique.')
    return redirect_with_tab(request, 'produits')


# =============================================
# PRIORITÉ - CRUD
# =============================================
@require_POST
def priorite_create(request):
    nom = request.POST.get('nom')
    niveau = request.POST.get('niveau', 0)
    if not nom:
        messages.error(request, 'Le nom est obligatoire.')
        return redirect('demandes:configuration_demandes')
    if Priorite.objects.filter(nom__iexact=nom).exists():
        messages.error(request, 'Cette priorité existe déjà.')
        return redirect('demandes:configuration_demandes')
    try:
        Priorite.objects.create(nom=nom, niveau=int(niveau))
        messages.success(request, f'Priorité "{nom}" ajoutée.')
    except Exception as e:
        logger.error(f"Erreur création priorité: {str(e)}")
        messages.error(request, 'Erreur technique.')
    return redirect('demandes:configuration_demandes')


@require_POST
def priorite_update(request):
    priorite_id = request.POST.get('priorite_id')
    nom = request.POST.get('nom')
    niveau = request.POST.get('niveau', 0)
    if not all([priorite_id, nom]):
        messages.error(request, 'Données manquantes.')
        return redirect('demandes:configuration_demandes')
    try:
        obj = get_object_or_404(Priorite, id=priorite_id)
        if Priorite.objects.filter(nom__iexact=nom).exclude(id=priorite_id).exists():
            messages.error(request, 'Un nom identique existe déjà.')
            return redirect('demandes:configuration_demandes')
        obj.nom = nom
        obj.niveau = int(niveau)
        obj.save()
        messages.success(request, 'Priorité mise à jour.')
    except Exception as e:
        logger.error(f"Erreur modification priorité: {str(e)}")
        messages.error(request, 'Erreur technique.')
    return redirect('demandes:configuration_demandes')


@require_POST
def priorite_delete(request):
    priorite_id = request.POST.get('priorite_id')
    if not priorite_id:
        messages.error(request, 'ID manquant.')
        return redirect('demandes:configuration_demandes')
    try:
        obj = get_object_or_404(Priorite, id=priorite_id)
        obj.delete()
        messages.success(request, 'Priorité supprimée.')
    except Exception as e:
        logger.error(f"Erreur suppression priorité: {str(e)}")
        messages.error(request, 'Erreur technique.')
    return redirect('demandes:configuration_demandes')


# =============================================
# STATUT - CRUD
# =============================================
@require_POST
def statut_create(request):
    nom = request.POST.get('nom')
    couleur = request.POST.get('couleur', '')
    if not nom:
        messages.error(request, 'Le nom est obligatoire.')
        return redirect('demandes:configuration_demandes')
    if Statut.objects.filter(nom__iexact=nom).exists():
        messages.error(request, 'Ce statut existe déjà.')
        return redirect('demandes:configuration_demandes')
    try:
        Statut.objects.create(nom=nom, couleur=couleur)
        messages.success(request, f'Statut "{nom}" ajouté.')
    except Exception as e:
        logger.error(f"Erreur création statut: {str(e)}")
        messages.error(request, 'Erreur technique.')
    return redirect('demandes:configuration_demandes')


@require_POST
def statut_update(request):
    statut_id = request.POST.get('statut_id')
    nom = request.POST.get('nom')
    couleur = request.POST.get('couleur', '')
    category = request.POST.get('category', 'active')  # Add this line to get the category
    
    if not all([statut_id, nom]):
        messages.error(request, 'Données manquantes.')
        return redirect('demandes:configuration_demandes')
    
    try:
        obj = get_object_or_404(Statut, id=statut_id)
        if Statut.objects.filter(nom__iexact=nom).exclude(id=statut_id).exists():
            messages.error(request, 'Un statut identique existe déjà.')
            return redirect('demandes:configuration_demandes')
        
        obj.nom = nom
        obj.couleur = couleur
        obj.category = category  # Add this line to update the category
        obj.save()
        
        messages.success(request, 'Statut mis à jour.')
    except Exception as e:
        logger.error(f"Erreur modification statut: {str(e)}")
        messages.error(request, 'Erreur technique.')
    
    return redirect('demandes:configuration_demandes')
@require_POST
def statut_delete(request):
    statut_id = request.POST.get('statut_id')
    if not statut_id:
        messages.error(request, 'ID manquant.')
        return redirect('demandes:configuration_demandes')
    try:
        obj = get_object_or_404(Statut, id=statut_id)
        obj.delete()
        messages.success(request, 'Statut supprimé.')
    except Exception as e:
        logger.error(f"Erreur suppression statut: {str(e)}")
        messages.error(request, 'Erreur technique.')
    return redirect('demandes:configuration_demandes')


# =============================================
# PATIENT - CRUD
# =============================================
@require_POST
def patient_create(request):
    nom = request.POST.get('nom')
    prenom = request.POST.get('prenom')
    date_naissance = request.POST.get('date_naissance')
    sexe = request.POST.get('sexe')
    
    if not all([nom, prenom]):
        messages.error(request, 'Le nom et le prénom sont obligatoires.')
        return redirect('demandes:configuration_demandes')
    
    try:
        DemandePatientModel.objects.create(
            nom=nom,
            prenom=prenom,
            date_naissance=date_naissance if date_naissance else None,
            sexe=sexe if sexe else None
        )
        messages.success(request, f'Patient "{prenom} {nom}" ajouté.')
    except Exception as e:
        logger.error(f"Erreur création patient: {str(e)}")
        messages.error(request, 'Erreur technique.')
    
    return redirect('demandes:configuration_demandes')


@require_POST
def patient_update(request):
    patient_id = request.POST.get('patient_id')
    nom = request.POST.get('nom')
    prenom = request.POST.get('prenom')
    date_naissance = request.POST.get('date_naissance')
    sexe = request.POST.get('sexe')
    
    if not all([patient_id, nom, prenom]):
        messages.error(request, 'Données manquantes.')
        return redirect('demandes:configuration_demandes')
    
    try:
        patient = get_object_or_404(DemandePatientModel, id=patient_id)
        patient.nom = nom
        patient.prenom = prenom
        patient.date_naissance = date_naissance if date_naissance else None
        patient.sexe = sexe if sexe else None
        patient.save()
        messages.success(request, f'Patient "{prenom} {nom}" mis à jour.')
    except Exception as e:
        logger.error(f"Erreur modification patient: {str(e)}")
        messages.error(request, 'Erreur technique.')
    
    return redirect('demandes:configuration_demandes')


@require_POST
def patient_delete(request):
    patient_id = request.POST.get('patient_id')
    if not patient_id:
        messages.error(request, 'ID patient manquant.')
        return redirect('demandes:configuration_demandes')
    
    try:
        patient = get_object_or_404(DemandePatientModel, id=patient_id)
        nom_complet = f"{patient.prenom} {patient.nom}"
        patient.delete()
        messages.success(request, f'Patient "{nom_complet}" supprimé.')
    except Exception as e:
        logger.error(f"Erreur suppression patient: {str(e)}")
        messages.error(request, 'Erreur technique.')
    
    return redirect('demandes:configuration_demandes')


# =============================================
# PRESTATAIRE - CRUD
# =============================================
@require_POST
def prestataire_create(request):
    nom = request.POST.get('nom')
    contact = request.POST.get('contact', '')
    adresse = request.POST.get('adresse', '')
    
    if not nom:
        messages.error(request, 'Le nom du prestataire est obligatoire.')
        return redirect_with_tab(request, 'prestataires')
    
    try:
        Supplier.objects.create(
            nom=nom,
            contact=contact,
            adresse=adresse,
            actif=True
        )
        messages.success(request, f'Prestataire "{nom}" ajouté.')
    except Exception as e:
        logger.error(f"Erreur création prestataire: {str(e)}")
        messages.error(request, 'Erreur technique.')
    
    return redirect_with_tab(request, 'prestataires')


@require_POST
def prestataire_update(request):
    prestataire_id = request.POST.get('prestataire_id')
    nom = request.POST.get('nom')
    contact = request.POST.get('contact', '')
    adresse = request.POST.get('adresse', '')
    
    if not all([prestataire_id, nom]):
        messages.error(request, 'Données manquantes.')
        return redirect_with_tab(request, 'prestataires')
    
    try:
        prestataire = get_object_or_404(Supplier, id=prestataire_id)
        prestataire.nom = nom
        prestataire.contact = contact
        prestataire.adresse = adresse
        prestataire.save()
        messages.success(request, f'Prestataire "{nom}" mis à jour.')
    except Exception as e:
        logger.error(f"Erreur modification prestataire: {str(e)}")
        messages.error(request, 'Erreur technique.')
    
    return redirect_with_tab(request, 'prestataires')


@require_POST
def prestataire_delete(request):
    prestataire_id = request.POST.get('prestataire_id')
    if not prestataire_id:
        messages.error(request, 'ID prestataire manquant.')
        return redirect_with_tab(request, 'prestataires')
    
    try:
        prestataire = get_object_or_404(Supplier, id=prestataire_id)
        nom = prestataire.nom
        prestataire.delete()
        messages.success(request, f'Prestataire "{nom}" supprimé.')
    except Exception as e:
        logger.error(f"Erreur suppression prestataire: {str(e)}")
        messages.error(request, 'Erreur technique.')
    
    return redirect_with_tab(request, 'prestataires')


# =============================================
# DEPARTEMENT - CRUD
# =============================================
@require_POST
def departement_create(request):
    name = request.POST.get('name')
    description = request.POST.get('description', '')
    if not name:
        messages.error(request, 'Le nom du département est obligatoire.')
        return redirect_with_tab(request, 'departements')
    try:
        Department.objects.create(name=name, description=description)
        messages.success(request, f'Département "{name}" ajouté.')
    except Exception as e:
        logger.error(f"Erreur création département: {str(e)}")
        messages.error(request, 'Erreur technique.')
    return redirect_with_tab(request, 'departements')


@require_POST
def departement_update(request):
    departement_id = request.POST.get('departement_id')
    name = request.POST.get('name')
    description = request.POST.get('description', '')
    if not all([departement_id, name]):
        messages.error(request, 'Données manquantes.')
        return redirect_with_tab(request, 'departements')
    try:
        departement = get_object_or_404(Department, id=departement_id)
        departement.name = name
        departement.description = description
        departement.save()
        messages.success(request, 'Département mis à jour.')
    except Exception as e:
        logger.error(f"Erreur modification département: {str(e)}")
        messages.error(request, 'Erreur technique.')
    return redirect_with_tab(request, 'departements')


@require_POST
def departement_delete(request):
    departement_id = request.POST.get('departement_id')
    if not departement_id:
        messages.error(request, 'ID département manquant.')
        return redirect_with_tab(request, 'departements')
    try:
        departement = get_object_or_404(Department, id=departement_id)
        name = departement.name
        departement.delete()
        messages.success(request, f'Département "{name}" supprimé.')
    except Exception as e:
        logger.error(f"Erreur suppression département: {str(e)}")
        messages.error(request, 'Erreur technique.')
    return redirect_with_tab(request, 'departements')


# =============================================
# ROUTER PRINCIPAL - configuration
# =============================================
def configuration_demandes(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        active_tab = request.POST.get('active_tab', 'produits')
        
        # Ajouter l'onglet actif à la requête pour que les fonctions CRUD puissent l'utiliser
        request.active_tab = active_tab
        
        mapping = {
            'add_produit': produit_create,
            'edit_produit': produit_update,
            'delete_produit': produit_delete,
            'add_priorite': priorite_create,
            'edit_priorite': priorite_update,
            'delete_priorite': priorite_delete,
            'add_statut': statut_create,
            'edit_statut': statut_update,
            'delete_statut': statut_delete,
            'add_patient': patient_create,
            'edit_patient': patient_update,
            'delete_patient': patient_delete,
            'add_prestataire': prestataire_create,
            'edit_prestataire': prestataire_update,
            'delete_prestataire': prestataire_delete,
            'add_departement': departement_create,
            'edit_departement': departement_update,
            'delete_departement': departement_delete,
        }
        handler = mapping.get(action)
        if handler:
            return handler(request)
        else:
            messages.error(request, 'Action inconnue.')
    
    # Récupérer l'onglet actif depuis GET ou POST
    active_tab = request.GET.get('active_tab') or request.POST.get('active_tab', 'produits')
    return configuration_list(request, active_tab)


# =============================================
# GESTION DES DEMANDES INTERNES
# =============================================

def demandes_internes_list(request):
    """
    List all internal demands with filtering and pagination capabilities
    Handles both regular requests and AJAX requests for table updates
    """
    try:
        query = request.GET.get('q', '').strip()
        source_id = request.GET.get('source_id')
        dest_id = request.GET.get('dest_id')
        
        # Récupérer TOUTES les demandes (sans filtre de statut pour le moment)
        demandes = DemandeInterne.objects.select_related(
            'departement_source',
            'departement_destinataire',
            'priorite',
            'statut',
        ).prefetch_related(
            'produits_dans_demande__produit'
        ).order_by('-created_at')

        # Debug: Afficher le nombre total de demandes
        total_demandes = demandes.count()
        print(f"DEBUG: Total demandes trouvées: {total_demandes}")
        
        # Appliquer les filtres
        if query:
            demandes = demandes.filter(description__icontains=query)
            print(f"DEBUG: Après filtre description '{query}': {demandes.count()}")
        if source_id:
            demandes = demandes.filter(departement_source_id=source_id)
            print(f"DEBUG: Après filtre source_id {source_id}: {demandes.count()}")
        if dest_id:
            demandes = demandes.filter(departement_destinataire_id=dest_id)
            print(f"DEBUG: Après filtre dest_id {dest_id}: {demandes.count()}")

        # Pagination - Toujours 5 éléments par page
        paginator = Paginator(demandes, 5)
        page_number = request.GET.get('page')
        
        try:
            demandes_page = paginator.page(page_number)
        except PageNotAnInteger:
            demandes_page = paginator.page(1)
        except EmptyPage:
            demandes_page = paginator.page(paginator.num_pages)

        print(f"DEBUG: Demandes sur la page {demandes_page.number}: {len(demandes_page)}")

        context = {
            'demandes': demandes_page,
            'query': query,
            'source_id': source_id,
            'dest_id': dest_id,
            'departements': Department.objects.all().order_by('name'),
            'priorites': Priorite.objects.all().order_by('niveau'),
            'statuts': Statut.objects.all().order_by('nom'),
            'produits_internes': Produit.objects.filter(
                type_demande__iexact='interne',
                disponible=True
            ).order_by('nom'),
        }

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html_content = render_to_string('demandes_internes.html', context)
            import re
            match = re.search(r'<tbody id="demandes-table">(.*?)</tbody>', html_content, re.DOTALL)
            if match:
                return JsonResponse({'html': match.group(1)})
            else:
                return JsonResponse({'error': 'Impossible de trouver le tableau'}, status=500)

        return render(request, 'demandes_internes.html', context)

    except Exception as e:
        import traceback
        traceback.print_exc()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=500)
        raise

@require_POST
@transaction.atomic
def demande_create(request):
    try:
        source = get_object_or_404(Department, id=request.POST.get('departement_source'))
        dest = get_object_or_404(Department, id=request.POST.get('departement_destinataire'))
        if source == dest:
            messages.error(request, "❌ La source et le destinataire ne peuvent pas être identiques.")
            return redirect('demandes_internes')

        d = DemandeInterne.objects.create(
            departement_source=source,
            departement_destinataire=dest,
            priorite=get_object_or_404(Priorite, id=request.POST.get('priorite')),
            statut=get_object_or_404(Statut, id=request.POST.get('statut')),
            description=request.POST.get('description', ''),
            date_souhaitee=request.POST.get('date_souhaitee') or None,
        )

        product_ids = request.POST.getlist('produits[]')
        quantities = request.POST.getlist('quantites[]')

        seen = set()
        for pid, qty in zip(product_ids, quantities):
            if not pid or not qty.isdigit() or int(qty) <= 0:
                continue
            if pid in seen:
                messages.warning(request, f"⚠️ Le produit ID {pid} est en double. Ignoré.")
                continue
            produit = get_object_or_404(Produit, id=pid, type_demande__iexact='interne')
            DemandeProduit.objects.create(
                demande_interne=d,
                produit=produit,
                quantite=int(qty)
            )
            seen.add(pid)

        messages.success(request, "✅ Demande créée avec succès.")
    except Exception as e:
        messages.error(request, f"❌ Erreur : {str(e)}")
    return redirect('demandes:demandes_internes')

@require_POST
@transaction.atomic
def demande_update(request):
    try:
        d = get_object_or_404(DemandeInterne, id=request.POST.get('demande_id'))
        source = get_object_or_404(Department, id=request.POST.get('departement_source'))
        dest = get_object_or_404(Department, id=request.POST.get('departement_destinataire'))

        if source == dest:
            messages.error(request, "❌ La source et le destinataire ne peuvent pas être identiques.")
            return redirect('demandes_internes')

        d.departement_source = source
        d.departement_destinataire = dest
        d.priorite = get_object_or_404(Priorite, id=request.POST.get('priorite'))
        d.statut = get_object_or_404(Statut, id=request.POST.get('statut'))
        d.description = request.POST.get('description', '')
        d.date_souhaitee = request.POST.get('date_souhaitee') or None
        d.save()

        # ✅ Delete old products — use demande_interne
        DemandeProduit.objects.filter(demande_interne=d).delete()

        product_ids = request.POST.getlist('produits[]')
        quantities = request.POST.getlist('quantites[]')

        seen = set()
        for pid, qty in zip(product_ids, quantities):
            if not pid or not qty.isdigit() or int(qty) <= 0:
                continue
            if pid in seen:
                messages.warning(request, f"⚠️ Le produit ID {pid} est en double. Ignoré.")
                continue
            produit = get_object_or_404(Produit, id=pid, type_demande__iexact='interne')
            # ✅ Link to demande_interne
            DemandeProduit.objects.create(
                demande_interne=d,
                produit=produit,
                quantite=int(qty)
            )
            seen.add(pid)

        messages.success(request, "✅ Demande mise à jour.")
    except Exception as e:
        logger.error("❌ Error updating demande: %s", str(e))
        messages.error(request, f"❌ Erreur : {str(e)}")

    return redirect('demandes:demandes_internes')
@require_POST
def demande_delete(request):
    try:
        demande_id = request.POST.get('demande_id')
        d = get_object_or_404(DemandeInterne, id=demande_id)
        desc = d.description
        d.delete()
        messages.success(request, f"✅ Demande '{desc}' supprimée.")
    except Exception as e:
        messages.error(request, f"❌ Erreur : {str(e)}")
    return redirect('demandes:demandes_internes')


def demandes_internes(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            return demande_create(request)
        elif action == 'edit':
            return demande_update(request)
        elif action == 'delete':
            return demande_delete(request)
        else:
            messages.error(request, '❌ Action inconnue.')
    return demandes_internes_list(request)
# =============================================
# GESTION DES DEMANDES PATIENT
# =============================================

def demandes_patients_list(request):
    """
    List all patient demands with filtering and pagination capabilities
    Handles both regular requests and AJAX requests for table updates
    """
    try:
        query = request.GET.get('q', '').strip()
        patient_id = request.GET.get('patient_id')
        priorite_id = request.GET.get('priorite_id')
        
        # Récupérer TOUTES les demandes (sans filtre de statut pour le moment)
        demandes = DemandePatient.objects.select_related(
            'patient',
            'priorite',
            'statut',
            'prestataire'
        ).prefetch_related(
            'produits_dans_demande__produit'
        ).order_by('-created_at')

        # Debug: Afficher le nombre total de demandes
        total_demandes = demandes.count()
        print(f"DEBUG: Total demandes patient trouvées: {total_demandes}")
        
        # Appliquer les filtres
        if query:
            demandes = demandes.filter(description__icontains=query)
            print(f"DEBUG: Après filtre description '{query}': {demandes.count()}")
        if patient_id:
            demandes = demandes.filter(patient_id=patient_id)
            print(f"DEBUG: Après filtre patient_id {patient_id}: {demandes.count()}")
        if priorite_id:
            demandes = demandes.filter(priorite_id=priorite_id)
            print(f"DEBUG: Après filtre priorite_id {priorite_id}: {demandes.count()}")

        # Pagination - Toujours 5 éléments par page
        paginator = Paginator(demandes, 5)
        page_number = request.GET.get('page')
        
        try:
            demandes_page = paginator.page(page_number)
        except PageNotAnInteger:
            demandes_page = paginator.page(1)
        except EmptyPage:
            demandes_page = paginator.page(paginator.num_pages)

        print(f"DEBUG: Demandes patient sur la page {demandes_page.number}: {len(demandes_page)}")

        context = {
            'demandes': demandes_page,
            'query': query,
            'patient_id': patient_id,
            'priorite_id': priorite_id,
            'patients': DemandePatientModel.objects.all().order_by('nom', 'prenom'),
            'prestataires': Supplier.objects.all().order_by('name'),
            'priorites': Priorite.objects.all().order_by('niveau'),
            'statuts': Statut.objects.all().order_by('nom'),
            'produits_patient': Produit.objects.filter(
                type_demande__iexact='patient',
                disponible=True
            ).order_by('nom'),
        }

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html_content = render_to_string('demande_patient.html', context)
            import re
            match = re.search(r'<tbody id="demandes-table">(.*?)</tbody>', html_content, re.DOTALL)
            if match:
                return JsonResponse({'html': match.group(1)})
            else:
                return JsonResponse({'error': 'Impossible de trouver le tableau'}, status=500)

        return render(request, 'demande_patient.html', context)

    except Exception as e:
        import traceback
        traceback.print_exc()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=500)
        raise
@require_POST
@transaction.atomic
def demande_patient_create(request):
    try:
        patient = get_object_or_404(DemandePatientModel, id=request.POST.get('patient'))
        d = DemandePatient.objects.create(
            patient=patient,
            prestataire=get_object_or_404(Supplier, id=request.POST.get('prestataire')) if request.POST.get('prestataire') else None,
            priorite=get_object_or_404(Priorite, id=request.POST.get('priorite')),
            statut=get_object_or_404(Statut, id=request.POST.get('statut')),
            description=request.POST.get('description', ''),
            date_souhaitee=request.POST.get('date_souhaitee') or None,
        )

        product_ids = request.POST.getlist('produits[]')
        quantities = request.POST.getlist('quantites[]')

        seen = set()
        for pid, qty in zip(product_ids, quantities):
            if not pid or not qty.isdigit() or int(qty) <= 0:
                continue
            if pid in seen:
                messages.warning(request, f"⚠️ Le produit ID {pid} est en double. Ignoré.")
                continue
            produit = get_object_or_404(Produit, id=pid, type_demande__iexact='patient')
            DemandeProduit.objects.create(
                demande_patient=d,
                produit=produit,
                quantite=int(qty)
            )
            seen.add(pid)

        messages.success(request, "✅ Demande patient créée avec succès.")
    except Exception as e:
        messages.error(request, f"❌ Erreur : {str(e)}")
    return redirect('demandes:demandes_patients')
@require_POST
@transaction.atomic
def demande_patient_update(request):
    try:
        d = get_object_or_404(DemandePatient, id=request.POST.get('demande_id'))
        patient = get_object_or_404(DemandePatientModel, id=request.POST.get('patient'))
        prestataire = get_object_or_404(Supplier, id=request.POST.get('prestataire')) if request.POST.get('prestataire') else None

        d.patient = patient
        d.prestataire = prestataire
        d.priorite = get_object_or_404(Priorite, id=request.POST.get('priorite'))
        d.statut = get_object_or_404(Statut, id=request.POST.get('statut'))
        d.description = request.POST.get('description', '')
        d.date_souhaitee = request.POST.get('date_souhaitee') or None
        d.save()

        # ✅ Delete old products — use demande_patient
        DemandeProduit.objects.filter(demande_patient=d).delete()

        product_ids = request.POST.getlist('produits[]')
        quantities = request.POST.getlist('quantites[]')

        seen = set()
        for pid, qty in zip(product_ids, quantities):
            if not pid or not qty.isdigit() or int(qty) <= 0:
                continue
            if pid in seen:
                messages.warning(request, f"⚠️ Le produit ID {pid} est en double. Ignoré.")
                continue
            produit = get_object_or_404(Produit, id=pid, type_demande__iexact='patient')
            # ✅ Link to demande_patient
            DemandeProduit.objects.create(
                demande_patient=d,
                produit=produit,
                quantite=int(qty)
            )
            seen.add(pid)

        messages.success(request, "✅ Demande patient mise à jour.")
    except Exception as e:
        messages.error(request, f"❌ Erreur : {str(e)}")

    return redirect('demandes:demandes_patients')

@require_POST
def demande_patient_delete(request):
    try:
        demande_id = request.POST.get('demande_id')
        d = get_object_or_404(DemandePatient, id=demande_id)
        desc = d.description
        d.delete()
        messages.success(request, f"✅ Demande patient '{desc}' supprimée.")
    except Exception as e:
        messages.error(request, f"❌ Erreur : {str(e)}")
    return redirect('demandes:demandes_patients')


def demandes_patients(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            return demande_patient_create(request)
        elif action == 'edit':
            return demande_patient_update(request)
        elif action == 'delete':
            return demande_patient_delete(request)
        else:
            messages.error(request, '❌ Action inconnue.')
    return demandes_patients_list(request)


def statistique_demande_view(request):
    # Fetch stats by category
    active_stats = Statut.objects.filter(category='active')
    terminated_stats = Statut.objects.filter(category='terminated')
    cancelled_stats = Statut.objects.filter(category='cancelled')

    total_internes = DemandeInterne.objects.count()
    total_patients = DemandePatient.objects.count()
    total_demandes = total_internes + total_patients

    # Active: NOT in terminated or cancelled
    active_internes = DemandeInterne.objects.exclude(
        statut__in=list(terminated_stats) + list(cancelled_stats)
    ).count()
    active_patients = DemandePatient.objects.exclude(
        statut__in=list(terminated_stats) + list(cancelled_stats)
    ).count()
    active_demandes = active_internes + active_patients

    # Terminated
    expired_demandes = (
        DemandeInterne.objects.filter(statut__in=terminated_stats).count() +
        DemandePatient.objects.filter(statut__in=terminated_stats).count()
    )

    # Cancelled
    archived_demandes = (
        DemandeInterne.objects.filter(statut__in=cancelled_stats).count() +
        DemandePatient.objects.filter(statut__in=cancelled_stats).count()
    )

    def safe_percent(part, total):
        return round((part / total) * 100, 1) if total > 0 else 0.0

    context = {
        'total_demandes': total_demandes,
        'total_internes': total_internes,
        'total_patients': total_patients,
        'active_demandes': active_demandes,
        'expired_demandes': expired_demandes,
        'archived_demandes': archived_demandes,
        'active_percent': safe_percent(active_demandes, total_demandes),
        'expired_percent': safe_percent(expired_demandes, total_demandes),
        'archived_percent': safe_percent(archived_demandes, total_demandes),
    }

    return render(request, 'statistique_demande.html', context)


# API Views
def demande_stats_api(request):
    interne_stats = list(DemandeInterne.objects.values('priorite__nom').annotate(count=Count('id')))
    patient_stats = list(DemandePatient.objects.values('priorite__nom').annotate(count=Count('id')))
    
    from collections import defaultdict
    merged = defaultdict(int)
    for item in interne_stats:
        merged[item['priorite__nom']] += item['count']
    for item in patient_stats:
        merged[item['priorite__nom']] += item['count']
    
    priority_data = [{'label': k, 'count': v} for k, v in merged.items()]
    
    dept_stats = list(DemandeInterne.objects.values('departement_destinataire__name').annotate(count=Count('id')).order_by('-count')[:5])
    
    return JsonResponse({
        'priority_data': priority_data,
        'department_data': [
            {'name': d['departement_destinataire__name'] or 'Autre', 'count': d['count']}
            for d in dept_stats
        ]
    })


def status_stats_api(request):
    active_stats = Statut.objects.filter(category='active')
    terminated_stats = Statut.objects.filter(category='terminated')
    cancelled_stats = Statut.objects.filter(category='cancelled')

    stats = {
        'active': 0,
        'terminated': 0,
        'cancelled': 0
    }

    for d in DemandeInterne.objects.all():
        if d.statut in terminated_stats:
            stats['terminated'] += 1
        elif d.statut in cancelled_stats:
            stats['cancelled'] += 1
        else:
            stats['active'] += 1

    for d in DemandePatient.objects.all():
        if d.statut in terminated_stats:
            stats['terminated'] += 1
        elif d.statut in cancelled_stats:
            stats['cancelled'] += 1
        else:
            stats['active'] += 1

    return JsonResponse(stats)


# =============================================
# STATISTIQUES DÉTAILLÉES
# =============================================
def statistiques_demandes_view(request):
    """Vue pour afficher les statistiques détaillées des demandes"""
    
    # Statistiques des demandes internes
    total_demandes_internes = DemandeInterne.objects.count()
    demandes_internes_en_cours = DemandeInterne.objects.filter(statut__category='active').count()
    demandes_internes_terminees = DemandeInterne.objects.filter(statut__category='terminated').count()
    demandes_internes_urgentes = DemandeInterne.objects.filter(priorite__niveau__gte=4).count()
    demandes_internes_en_attente = DemandeInterne.objects.filter(statut__category='pending').count()
    demandes_internes_annulees = DemandeInterne.objects.filter(statut__category='cancelled').count()
    
    # Statistiques des demandes patients
    total_demandes_patients = DemandePatient.objects.count()
    patients_actifs = DemandePatient.objects.filter(statut__category='active').count()
    nouveaux_patients = DemandePatientModel.objects.filter(
        demandepatient__created_at__gte=timezone.now() - timezone.timedelta(days=30)
    ).distinct().count()
    patients_recurrents = DemandePatientModel.objects.annotate(
        demandes_count=Count('demandepatient')
    ).filter(demandes_count__gt=1).count()
    
    # Statistiques par département
    demandes_par_departement = DemandeInterne.objects.values('departement_destinataire__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Statistiques par priorité
    demandes_par_priorite = DemandeInterne.objects.values('priorite__nom').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Top des départements
    top_departements = DemandeInterne.objects.values('departement_destinataire__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Top des patients
    top_patients = DemandePatientModel.objects.annotate(
        demandes_count=Count('demandepatient')
    ).order_by('-demandes_count')[:5]
    
    # Types de demandes patients (toutes les demandes patients sont du même type)
    types_demandes_patients = [{'nom': 'Demande Patient', 'count': total_demandes_patients}]
    
    # Répartition des patients par nombre de demandes
    patients_1_demande = DemandePatientModel.objects.annotate(
        demandes_count=Count('demandepatient')
    ).filter(demandes_count=1).count()
    
    patients_2_3_demandes = DemandePatientModel.objects.annotate(
        demandes_count=Count('demandepatient')
    ).filter(demandes_count__in=[2, 3]).count()
    
    patients_4_5_demandes = DemandePatientModel.objects.annotate(
        demandes_count=Count('demandepatient')
    ).filter(demandes_count__in=[4, 5]).count()
    
    patients_6_plus_demandes = DemandePatientModel.objects.annotate(
        demandes_count=Count('demandepatient')
    ).filter(demandes_count__gte=6).count()
    
    # Calculs de performance
    try:
        # Temps moyen de traitement (en heures)
        demandes_terminees = DemandeInterne.objects.filter(
            statut__category='terminated',
            date_fin__isnull=False,
            date_creation__isnull=False
        )
        
        total_heures = 0
        count = 0
        for demande in demandes_terminees:
            if demande.date_fin and demande.date_creation:
                delta = demande.date_fin - demande.date_creation
                total_heures += delta.total_seconds() / 3600
                count += 1
        
        temps_moyen_traitement = total_heures / count if count > 0 else 0
        
        # Taux de respect des délais
        demandes_delai_respecte = demandes_terminees.filter(
            date_fin__lte=F('date_limite')
        ).count() if hasattr(DemandeInterne, 'date_limite') else 0
        
        taux_resolution_delai = (demandes_delai_respecte / count * 100) if count > 0 else 0
        
    except:
        temps_moyen_traitement = 0
        taux_resolution_delai = 0
    
    # Métriques pour les patients
    try:
        # Temps moyen de réponse aux demandes patients
        demandes_patients_terminees = DemandePatient.objects.filter(
            statut__category='terminated',
            date_fin__isnull=False,
            date_creation__isnull=False
        )
        
        total_heures_patient = 0
        count_patient = 0
        for demande in demandes_patients_terminees:
            if demande.date_fin and demande.date_creation:
                delta = demande.date_fin - demande.date_creation
                total_heures_patient += delta.total_seconds() / 3600
                count_patient += 1
        
        temps_moyen_reponse_patient = total_heures_patient / count_patient if count_patient > 0 else 0
        
        # Taux de résolution des demandes patients
        taux_resolution_patient = (count_patient / total_demandes_patients * 100) if total_demandes_patients > 0 else 0
        
    except:
        temps_moyen_reponse_patient = 0
        taux_resolution_patient = 0
    
    context = {
        # Demandes internes
        'total_demandes_internes': total_demandes_internes,
        'demandes_internes_en_cours': demandes_internes_en_cours,
        'demandes_internes_terminees': demandes_internes_terminees,
        'demandes_internes_urgentes': demandes_internes_urgentes,
        'demandes_internes_en_attente': demandes_internes_en_attente,
        'demandes_internes_annulees': demandes_internes_annulees,
        
        # Demandes patients
        'total_demandes_patients': total_demandes_patients,
        'patients_actifs': patients_actifs,
        'nouveaux_patients': nouveaux_patients,
        'patients_recurrents': patients_recurrents,
        
        # Statistiques par catégorie
        'demandes_par_departement': demandes_par_departement,
        'demandes_par_priorite': demandes_par_priorite,
        'types_demandes_patients': types_demandes_patients,
        
        # Top des éléments
        'top_departements': top_departements,
        'top_patients': top_patients,
        
        # Répartition des patients
        'patients_1_demande': patients_1_demande,
        'patients_2_3_demandes': patients_2_3_demandes,
        'patients_4_5_demandes': patients_4_5_demandes,
        'patients_6_plus_demandes': patients_6_plus_demandes,
        
        # Métriques de performance
        'temps_moyen_traitement': temps_moyen_traitement,
        'taux_resolution_delai': taux_resolution_delai,
        'temps_moyen_reponse_patient': temps_moyen_reponse_patient,
        'taux_resolution_patient': taux_resolution_patient,
    }
    
    return render(request, 'statistiques_demandes.html', context)