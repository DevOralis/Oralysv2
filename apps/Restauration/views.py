import json
from django.core import serializers
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q, Count, F, ExpressionWrapper, fields
from django.contrib import messages
from django.db import transaction
from .models import Plat, Recette, LigneRecette, MenuStandard, Programme, ProgrammeJour, MenuPersonnalise, MenuSupplementaire, ProgrammeJourMenu
from apps.inventory.models import Product, Category
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from datetime import datetime, timedelta, date
from django.utils import timezone
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect
from .models import MenuPersonnalise, MenuSupplementaire
from .forms import MenuPersonnaliseForm, MenuSupplementaireForm, ProgrammeJourMenuForm, ProgrammeJourForm
from .forms import MenuStandardForm, ProgrammeForm, ProgrammeJourForm
from calendar import monthrange
from collections import defaultdict
from apps.hosting.models import Reservation, Companion
from apps.patient.models import Patient
from django.db.models import Q
from .models import Programme
from calendar import monthrange
from django.views.decorators.csrf import csrf_exempt


# Liste des menus standards
def menu_standard_list(request):
    from .models import MenuStandard, Plat
    from .mixins import PaginationMixin
    from datetime import datetime, timedelta, date
    from django.utils import timezone
    from django.http import JsonResponse
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            # Ajout d'un nouveau menu
            form = MenuStandardForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('menu_standard_list')
            else:
                # En cas d'erreur, afficher le formulaire avec les erreurs
                pass
                
        elif action == 'edit':
            # Modification d'un menu existant
            menu_id = request.POST.get('menu_id')
            try:
                menu = MenuStandard.objects.get(id=menu_id)
                form = MenuStandardForm(request.POST, instance=menu)
                if form.is_valid():
                    form.save()
                    return JsonResponse({'success': True, 'message': 'Menu modifié avec succès'})
                else:
                    return JsonResponse({'success': False, 'message': 'Données invalides'})
            except MenuStandard.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Menu non trouvé'})
                
        elif action == 'delete':
            # Suppression d'un menu
            menu_id = request.POST.get('menu_id')
            try:
                menu = MenuStandard.objects.get(id=menu_id)
                menu.delete()
                return JsonResponse({'success': True, 'message': 'Menu supprimé avec succès'})
            except MenuStandard.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Menu non trouvé'})
    else:
        form = MenuStandardForm()
    
    # Récupérer les paramètres de filtrage
    search_query = request.GET.get('q', '')
    repas_filter = request.GET.get('repas', '')
    periode_filter = request.GET.get('periode', '')
    
    # Construire le queryset de base
    menus = MenuStandard.objects.all()
    
    # Filtre par recherche (date ou repas)
    if search_query:
        menus = menus.filter(
            Q(date__icontains=search_query) |
            Q(repas__icontains=search_query)
        )
    
    # Filtre par type de repas
    if repas_filter:
        menus = menus.filter(repas=repas_filter)
    
    # Filtre par période
    if periode_filter:
        today = timezone.now().date()
        if periode_filter == 'aujourd\'hui':
            menus = menus.filter(date=today)
        elif periode_filter == 'semaine':
            # Cette semaine (lundi au dimanche)
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            menus = menus.filter(date__range=[start_of_week, end_of_week])
        elif periode_filter == 'mois':
            # Ce mois
            start_of_month = today.replace(day=1)
            end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            menus = menus.filter(date__range=[start_of_month, end_of_month])
    
    # Trier par date et repas
    menus = menus.order_by('date', 'repas')
    
    # Appliquer la pagination
    pagination_mixin = PaginationMixin()
    pagination_mixin.paginate_by = 5  # 5 menus par page
    
    queryset_page, paginator = pagination_mixin.paginate_queryset(menus, request)
    pagination_info = pagination_mixin.get_pagination_context(queryset_page, paginator, request)

    # Calculer le nombre de personnes (clients + accompagnants) pour chaque menu de la page
    for menu in queryset_page:
        if menu.date:
            # Récupère les réservations qui couvrent la date du menu
            reservations = Reservation.objects.filter(start_date__lte=menu.date, end_date__gte=menu.date)
            
            # Compter le nombre total de personnes (clients + accompagnants)
            total_personnes = 0
            for reservation in reservations:
                # 1 client par réservation
                total_personnes += 1
                # Ajouter le nombre d'accompagnants pour ce patient
                total_personnes += reservation.patient.companions.count()
            
            # Ajouter le nombre de personnes directement à l'objet menu
            menu.nb_personnes = total_personnes
        else:
            menu.nb_personnes = 0

    # Récupérer tous les plats disponibles pour le formulaire d'édition
    plats = Plat.objects.all().order_by('nom')

    return render(request, 'menu_standard_list.html', {
        'menus': queryset_page,
        'form': form,
        'pagination_info': pagination_info,
        'search_query': search_query,
        'repas_filter': repas_filter,
        'periode_filter': periode_filter,
        'plats': plats,
    })

# Création d'un menu standard
def menu_standard_create(request):
    if request.method == 'POST':
        form = MenuStandardForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('menu_standard_list')
    else:
        form = MenuStandardForm()
    return render(request, 'menu_standard_form.html', {'form': form, 'action': 'Créer'})

# Modification d'un menu standard
def menu_standard_update(request, pk):
    menu = get_object_or_404(MenuStandard, pk=pk)
    if request.method == 'POST':
        form = MenuStandardForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()
            return redirect('menu_standard_list')
    else:
        form = MenuStandardForm(instance=menu)
    return render(request, 'menu_standard_form.html', {'form': form, 'action': 'Modifier'})

# Suppression d'un menu standard
def menu_standard_delete(request, pk):
    menu = get_object_or_404(MenuStandard, pk=pk)
    if request.method == 'POST':
        menu.delete()
        return redirect('menu_standard_list')
    return render(request, 'menu_standard_confirm_delete.html', {'menu': menu})


def restauration_home(request):
    from .mixins import PaginationMixin
    from apps.inventory.models import Product, Category, UnitOfMesure
    from .models import Plat, Recette, LigneRecette
    
    # Récupérer tous les plats avec pagination
    plats = Plat.objects.all().order_by('nom')
    
    # Appliquer la pagination
    pagination_mixin = PaginationMixin()
    pagination_mixin.paginate_by = 5  # 5 plats par page
    
    queryset_page, paginator = pagination_mixin.paginate_queryset(plats, request)
    pagination_info = pagination_mixin.get_pagination_context(queryset_page, paginator, request)

    # Utiliser les modèles du module Inventory
    categories = Category.objects.all()
    ingredients = Product.objects.filter(active=True)  # Seulement les produits actifs
    uoms = UnitOfMesure.objects.all()  # Toutes les unités de mesure
    recettes = Recette.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            nom_plat = request.POST.get('nom')
            ingredient_ids = request.POST.getlist('ingredient[]')
            quantites = request.POST.getlist('quantite[]')

            if not nom_plat or not ingredient_ids or not quantites:
                messages.error(request, "Veuillez remplir tous les champs obligatoires pour le plat.")
                return redirect('restauration_home')

            try:
                with transaction.atomic():
                    plat = Plat.objects.create(nom=nom_plat)
                    # Créer automatiquement une recette pour le plat
                    recette = Recette.objects.create(plat=plat)

                    for i in range(len(ingredient_ids)):
                        ingredient = get_object_or_404(Product, product_id=ingredient_ids[i])
                        LigneRecette.objects.create(
                            recette=recette,
                            ingredient=ingredient,
                            quantite_par_portion=quantites[i]
                        )
                messages.success(request, f"Le plat '{nom_plat}' a été ajouté avec succès.")
            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout du plat : {e}")
            return redirect('restauration_home')

        elif action == 'edit':
            plat_id = request.POST.get('plat_id')
            nom_plat = request.POST.get('nom')
            ingredient_ids = request.POST.getlist('ingredient[]')
            quantites = request.POST.getlist('quantite[]')

            if not plat_id or not nom_plat or not ingredient_ids or not quantites:
                messages.error(request, "Veuillez remplir tous les champs obligatoires pour la modification du plat.")
                return redirect('restauration_home')

            try:
                with transaction.atomic():
                    plat = get_object_or_404(Plat, id=plat_id)
                    plat.nom = nom_plat
                    plat.save()

                    # Créer une recette si elle n'existe pas
                    if not hasattr(plat, 'recette') or not plat.recette:
                        recette = Recette.objects.create(plat=plat)
                    else:
                        # Supprimer les anciennes lignes de recette
                        plat.recette.lignes_recette.all().delete()
                        recette = plat.recette

                    # Ajouter les nouvelles lignes de recette
                    for i in range(len(ingredient_ids)):
                        ingredient = get_object_or_404(Product, product_id=ingredient_ids[i])
                        LigneRecette.objects.create(
                            recette=recette,
                            ingredient=ingredient,
                            quantite_par_portion=quantites[i]
                        )
                messages.success(request, f"Le plat '{nom_plat}' a été modifié avec succès.")
            except Exception as e:
                messages.error(request, f"Erreur lors de la modification du plat : {e}")
            return redirect('restauration_home')

        elif action == 'delete':
            plat_id = request.POST.get('plat_id')
            if not plat_id:
                messages.error(request, "ID du plat manquant pour la suppression.")
                return redirect('restauration_home')
            try:
                plat = get_object_or_404(Plat, id=plat_id)
                nom_plat = plat.nom
                plat.delete()
                messages.success(request, f"Le plat '{nom_plat}' a été supprimé avec succès.")
            except Exception as e:
                messages.error(request, f"Erreur lors de la suppression du plat : {e}")
            return redirect('restauration_home')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        query = request.GET.get('q', '')
        if query:
            try:
                # Filtrer les plats par nom
                plats_filtered = Plat.objects.filter(nom__icontains=query).order_by('nom')
                
                # Appliquer la pagination aux résultats filtrés
                pagination_mixin = PaginationMixin()
                pagination_mixin.paginate_by = 5
                queryset_page_filtered, paginator_filtered = pagination_mixin.paginate_queryset(plats_filtered, request)
                pagination_info_filtered = pagination_mixin.get_pagination_context(queryset_page_filtered, paginator_filtered, request)
                
                # Traiter les plats filtrés pour le JSON
                for plat in queryset_page_filtered:
                    lignes_list = []
                    try:
                        # Vérifier si le plat a une recette
                        if hasattr(plat, 'recette') and plat.recette:
                            lignes = plat.recette.lignes_recette.all()
                            for ligne in lignes:
                                lignes_list.append({
                                    'ingredient_id': ligne.ingredient.product_id,
                                    'quantite_par_portion': float(ligne.quantite_par_portion),
                                })
                    except:
                        # Si pas de recette, lignes_list reste vide
                        pass
                    plat.lignes_recette_json = json.dumps(lignes_list)
                
                return render(request, 'plats_table_partial.html', {
                    'plats': queryset_page_filtered,
                    'pagination_info': pagination_info_filtered,
                })
            except Exception as e:
                return JsonResponse({
                    'error': True,
                    'message': f'Erreur lors de la recherche: {str(e)}'
                }, status=500)
        else:
            # Si pas de requête, retourner tous les plats
            return render(request, 'plats_table_partial.html', {
                'plats': queryset_page,
                'pagination_info': pagination_info,
            })

    # Traiter les plats de la page courante
    for plat in queryset_page:
        lignes_list = []
        try:
            # Vérifier si le plat a une recette
            if hasattr(plat, 'recette') and plat.recette:
                lignes = plat.recette.lignes_recette.all()
                for ligne in lignes:
                    lignes_list.append({
                        'ingredient_id': ligne.ingredient.product_id,
                        'quantite_par_portion': float(ligne.quantite_par_portion),
                    })
        except:
            # Si pas de recette, lignes_list reste vide
            pass
        plat.lignes_recette_json = json.dumps(lignes_list)

    return render(request, 'plats.html', {
        'plats': queryset_page,
        'ingredients': ingredients,
        'categories': categories,
        'uoms': uoms,
        'pagination_info': pagination_info,
    })


# ==================== VUES POUR LA GESTION DES PROGRAMMES ====================

def programme_list(request):
    """Liste de tous les programmes avec pagination"""
    from .mixins import PaginationMixin
    from django.db.models import Q
    
    today = date.today()
    programmes = Programme.objects.all().order_by('-date_debut')
    
    # Récupérer les paramètres de recherche et filtrage
    search_query = request.GET.get('q', '')
    statut_filter = request.GET.get('statut', '')
    
    # Appliquer la recherche
    if search_query:
        programmes = programmes.filter(
            Q(nom__icontains=search_query) | 
            Q(lieu__icontains=search_query)
        )
    
    # Appliquer le filtre par statut
    if statut_filter:
        if statut_filter == 'en_cours':
            programmes = programmes.filter(date_debut__lte=today, date_fin__gte=today)
        elif statut_filter == 'planifie':
            programmes = programmes.filter(date_debut__gt=today)
        elif statut_filter == 'termine':
            programmes = programmes.filter(date_fin__lt=today)
    
    # Appliquer la pagination avec PaginationMixin
    pagination_mixin = PaginationMixin()
    pagination_mixin.paginate_by = 5  # 5 programmes par page
    
    queryset_page, paginator = pagination_mixin.paginate_queryset(programmes, request)
    pagination_info = pagination_mixin.get_pagination_context(queryset_page, paginator, request)
    
    return render(request, 'programme_list.html', {
        'programmes': queryset_page,
        'pagination_info': pagination_info,
        'today': today,
        'search_query': search_query,
        'statut_filter': statut_filter,
    })


def programme_create(request):
    """Création d'un nouveau programme"""
    if request.method == 'POST':
        form = ProgrammeForm(request.POST)
        if form.is_valid():
            programme = form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f"Le programme '{programme.nom}' a été créé avec succès."
                })
            messages.success(request, f"Le programme '{programme.nom}' a été créé avec succès.")
            return redirect('programme_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Erreur de validation du formulaire',
                    'errors': form.errors
                })
            # En cas de requête normale avec erreur, rediriger vers la liste
            messages.error(request, 'Erreur de validation du formulaire')
            return redirect('programme_list')
    
    # En cas de requête GET normale, rediriger vers la liste
    return redirect('programme_list')


def programme_update(request, pk):
    """Modification d'un programme existant"""
    programme = get_object_or_404(Programme, pk=pk)
    if request.method == 'POST':
        form = ProgrammeForm(request.POST, instance=programme)
        if form.is_valid():
            programme = form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f"Le programme '{programme.nom}' a été modifié avec succès."
                })
            messages.success(request, f"Le programme '{programme.nom}' a été modifié avec succès.")
            return redirect('programme_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Erreur de validation du formulaire',
                    'errors': form.errors
                })
            # En cas de requête normale avec erreur, rediriger vers la liste
            messages.error(request, 'Erreur de validation du formulaire')
            return redirect('programme_list')
    
    # En cas de requête GET normale, rediriger vers la liste
    return redirect('programme_list')


def programme_delete(request, pk):
    """Suppression d'un programme"""
    programme = get_object_or_404(Programme, pk=pk)
    if request.method == 'POST':
        nom = programme.nom
        programme.delete()
        messages.success(request, f"Le programme '{nom}' a été supprimé avec succès.")
        return redirect('programme_list')
    
    return render(request, 'programme_confirm_delete.html', {'programme': programme})


def programme_detail(request, pk):
    """Détails d'un programme avec ses jours"""
    programme = get_object_or_404(Programme, pk=pk)
    
    # Vérifier et corriger automatiquement les jours manquants
    delta = programme.date_fin - programme.date_debut
    total_jours_theorique = delta.days + 1
    jours_existants = programme.jours.count()
    
    # Si le nombre de jours ne correspond pas, essayer de corriger automatiquement
    if jours_existants != total_jours_theorique:
        print(f"DEBUG: Correction automatique pour {programme.nom}")
        print(f"DEBUG: Jours existants: {jours_existants}, Jours théoriques: {total_jours_theorique}")
        
        current_date = programme.date_debut
        jours_crees = 0
        
        while current_date <= programme.date_fin:
            if not ProgrammeJour.objects.filter(programme=programme, date=current_date).exists():
                try:
                    ProgrammeJour.objects.create(
                        programme=programme,
                        date=current_date
                    )
                    jours_crees += 1
                    print(f"DEBUG: Jour auto-créé: {current_date}")
                except Exception as e:
                    print(f"DEBUG: Erreur auto-création {current_date}: {e}")
            
            current_date += timedelta(days=1)
        
        if jours_crees > 0:
            print(f"DEBUG: {jours_crees} jours auto-créés pour {programme.nom}")
    
    # Récupérer les jours (après correction)
    jours = programme.jours.all().order_by('date')
    
    # Debug: Afficher les informations de débogage
    print(f"DEBUG: Programme {programme.nom} (ID: {pk})")
    print(f"DEBUG: Date début: {programme.date_debut}, Date fin: {programme.date_fin}")
    print(f"DEBUG: Nombre de jours trouvés: {jours.count()}")
    
    # Calculer les statistiques
    total_jours = jours.count()
    # Compter les jours avec menu personnalisé (pas les menus standards)
    jours_avec_menu = jours.filter(menu_personnalise__isnull=False).count()
    jours_sans_menu = total_jours - jours_avec_menu
    
    # Calculer le nombre de menus personnalisés (même valeur que jours_avec_menu)
    jours_avec_menu_personnalise = jours_avec_menu
    
    print(f"DEBUG: Total jours: {total_jours}")
    print(f"DEBUG: Jours avec menu: {jours_avec_menu}")
    print(f"DEBUG: Jours sans menu: {jours_sans_menu}")
    print(f"DEBUG: Jours avec menu personnalisé: {jours_avec_menu_personnalise}")
    
    print(f"DEBUG: Nombre théorique de jours: {total_jours_theorique}")
    print(f"DEBUG: Nombre réel de jours en base: {total_jours}")
    
    # Grouper les jours par semaine pour l'affichage
    semaines = {}
    for jour in jours:
        semaine = jour.date.isocalendar()[1]
        if semaine not in semaines:
            semaines[semaine] = []
        semaines[semaine].append(jour)
    
    return render(request, 'programme_detail.html', {
        'programme': programme,
        'jours': jours,
        'semaines': semaines,
        'total_jours': total_jours_theorique,
        'jours_avec_menu': jours_avec_menu,
        'jours_sans_menu': total_jours_theorique - jours_avec_menu,
        'jours_avec_menu_personnalise': jours_avec_menu_personnalise,
    })



def programme_generate_weeks(request, pk):
    """Générer automatiquement les jours pour un programme et lancer la configuration séquentielle"""
    programme = get_object_or_404(Programme, pk=pk)
    
    if request.method == 'POST':
        try:
            print(f"DEBUG: Génération des jours pour le programme {programme.nom}")
            print(f"DEBUG: Date début: {programme.date_debut}, Date fin: {programme.date_fin}")
            
            # Calculer toutes les dates entre date_debut et date_fin
            current_date = programme.date_debut
            jours_crees = 0
            jours_existants = 0
            
            while current_date <= programme.date_fin:
                print(f"DEBUG: Traitement de la date: {current_date}")
                # Vérifier si le jour existe déjà
                jour_existant = ProgrammeJour.objects.filter(programme=programme, date=current_date).first()
                
                if not jour_existant:
                    try:
                        ProgrammeJour.objects.create(
                            programme=programme,
                            date=current_date
                        )
                        jours_crees += 1
                        print(f"DEBUG: Jour créé pour {current_date}")
                    except Exception as create_error:
                        print(f"DEBUG: Erreur lors de la création du jour {current_date}: {create_error}")
                        messages.error(request, f"Erreur lors de la création du jour {current_date}: {create_error}")
                else:
                    jours_existants += 1
                    print(f"DEBUG: Jour existe déjà pour {current_date}")
                
                current_date += timedelta(days=1)
            
            # Calculer le nombre total de jours
            delta = programme.date_fin - programme.date_debut
            total_jours_theorique = delta.days + 1
            total_jours_reel = ProgrammeJour.objects.filter(programme=programme).count()
            
            print(f"DEBUG: Total jours créés: {jours_crees}")
            print(f"DEBUG: Total jours existants: {jours_existants}")
            print(f"DEBUG: Total jours théorique: {total_jours_theorique}")
            print(f"DEBUG: Total jours réel: {total_jours_reel}")
            
            if total_jours_reel == total_jours_theorique:
                messages.success(request, f"Tous les jours ({total_jours_reel}) sont maintenant disponibles. Configuration des menus en cours...")
                # Lancer la configuration séquentielle des menus
                return redirect('programme_configure_menus_sequential', pk=pk)
            else:
                messages.warning(request, f"Attention: {total_jours_reel}/{total_jours_theorique} jours créés. Certains jours pourraient être manquants.")
                return redirect('programme_detail', pk=pk)
            
        except Exception as e:
            print(f"DEBUG: Erreur générale: {e}")
            messages.error(request, f"Erreur lors de la génération des semaines : {e}")
            return redirect('programme_detail', pk=pk)
    
    # Rediriger vers la page de détail du programme si accès GET
    messages.info(request, "Veuillez utiliser le bouton 'Générer tous les jours' pour lancer la génération.")
    return redirect('programme_detail', pk=pk)


def programme_configure_menus_sequential(request, pk, jour_id=None):
    """Configuration séquentielle des menus pour chaque jour d'un programme"""
    programme = get_object_or_404(Programme, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save_and_next':
            # Enregistrer le menu pour le jour actuel et passer au suivant
            jour_id = request.POST.get('jour_id')
            programme_jour = get_object_or_404(ProgrammeJour, pk=jour_id, programme=programme)
            
            form = ProgrammeJourMenuForm(request.POST, programme_jour=programme_jour)
            if form.is_valid():
                # Extraire les données du formulaire, en excluant les champs ManyToMany
                cleaned_data = form.cleaned_data.copy()
                plats_data = cleaned_data.pop('plats', [])
                
                # Créer ou mettre à jour le menu pour ce jour
                menu, created = ProgrammeJourMenu.objects.get_or_create(
                    programme_jour=programme_jour,
                    defaults=cleaned_data
                )
                if not created:
                    # Mettre à jour les champs existants
                    for field, value in cleaned_data.items():
                        setattr(menu, field, value)
                    menu.save()
                
                # Gérer le champ ManyToMany séparément
                menu.plats.set(plats_data)
                
                messages.success(request, f"Menu configuré pour le {programme_jour.date.strftime('%d/%m/%Y')}")
                
                # Trouver le prochain jour sans menu
                next_jour = ProgrammeJour.objects.filter(
                    programme=programme,
                    date__gt=programme_jour.date
                ).exclude(
                    menu_personnalise__isnull=False
                ).order_by('date').first()
                
                if next_jour:
                    return redirect('programme_configure_menus_sequential_with_jour', pk=pk, jour_id=next_jour.pk)
                else:
                    messages.success(request, "Configuration terminée ! Tous les jours ont été configurés.")
                    return redirect('programme_detail', pk=pk)
            else:
                # Erreur de validation, rester sur le même jour
                messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
        
        elif action == 'skip_day':
            # Passer ce jour sans enregistrer
            jour_id = request.POST.get('jour_id')
            programme_jour = get_object_or_404(ProgrammeJour, pk=jour_id, programme=programme)
            
            messages.info(request, f"Jour {programme_jour.date.strftime('%d/%m/%Y')} ignoré")
            
            # Trouver le prochain jour sans menu
            next_jour = ProgrammeJour.objects.filter(
                programme=programme,
                date__gt=programme_jour.date
            ).exclude(
                menu_personnalise__isnull=False
            ).order_by('date').first()
            
            if next_jour:
                return redirect('programme_configure_menus_sequential_with_jour', pk=pk, jour_id=next_jour.pk)
            else:
                messages.success(request, "Configuration terminée ! Tous les jours ont été traités.")
                return redirect('programme_detail', pk=pk)
        
        elif action == 'cancel':
            # Annuler et retourner au détail du programme
            messages.info(request, "Configuration annulée.")
            return redirect('programme_detail', pk=pk)
    
    # GET request - afficher le formulaire pour le jour spécifié
    jour_id = jour_id or request.GET.get('jour_id')
    
    if jour_id:
        # Afficher le formulaire pour un jour spécifique
        programme_jour = get_object_or_404(ProgrammeJour, pk=jour_id, programme=programme)
        
        # Vérifier si un menu existe déjà pour ce jour
        try:
            menu_existant = programme_jour.menu_personnalise
            form = ProgrammeJourMenuForm(instance=menu_existant, programme_jour=programme_jour)
        except ProgrammeJourMenu.DoesNotExist:
            form = ProgrammeJourMenuForm(programme_jour=programme_jour)
        
        # Trouver le prochain jour sans menu pour l'affichage
        next_jour = ProgrammeJour.objects.filter(
            programme=programme,
            date__gt=programme_jour.date
        ).exclude(
            menu_personnalise__isnull=False
        ).order_by('date').first()
        
        # Calculer les statistiques pour l'affichage
        total_jours = programme.jours.count()
        jours_configures = programme.jours.filter(menu_personnalise__isnull=False).count()
        
        context = {
            'programme': programme,
            'programme_jour': programme_jour,
            'form': form,
            'next_jour': next_jour,
            'menu_exists': hasattr(programme_jour, 'menu_personnalise'),
            'total_jours': total_jours,
            'jours_configures': jours_configures,
        }
        
        return render(request, 'programme_configure_menu_sequential.html', context)
    
    else:
        # Trouver le premier jour sans menu
        premier_jour_sans_menu = ProgrammeJour.objects.filter(
            programme=programme
        ).exclude(
            menu_personnalise__isnull=False
        ).order_by('date').first()
        
        if premier_jour_sans_menu:
            return redirect('programme_configure_menus_sequential_with_jour', pk=pk, jour_id=premier_jour_sans_menu.pk)
        else:
            messages.success(request, "Tous les jours de ce programme ont déjà des menus configurés !")
            return redirect('programme_detail', pk=pk)



def menu_personnalise_list(request):
    """Liste des menus personnalisés avec pagination"""
    from .mixins import PaginationMixin
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            form = MenuPersonnaliseForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Menu personnalisé ajouté avec succès.")
                return redirect('menu_personnalise_list')
            else:
                messages.error(request, "Erreur lors de l'ajout du menu personnalisé.")
                
        elif action == 'edit':
            menu_id = request.POST.get('menu_id')
            try:
                menu = MenuPersonnalise.objects.get(id=menu_id)
                form = MenuPersonnaliseForm(request.POST, instance=menu)
                if form.is_valid():
                    form.save()
                    return JsonResponse({'success': True, 'message': 'Menu modifié avec succès'})
                else:
                    return JsonResponse({'success': False, 'message': 'Données invalides'})
            except MenuPersonnalise.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Menu non trouvé'})
                
        elif action == 'delete':
            menu_id = request.POST.get('menu_id')
            try:
                menu = MenuPersonnalise.objects.get(id=menu_id)
                menu.delete()
                return JsonResponse({'success': True, 'message': 'Menu supprimé avec succès'})
            except MenuPersonnalise.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Menu non trouvé'})
    else:
        form = MenuPersonnaliseForm()
    
    # Récupérer les paramètres de filtrage
    search_query = request.GET.get('q', '')
    repas_filter = request.GET.get('repas', '')
    
    # Construire le queryset de base
    menus = MenuPersonnalise.objects.all()
    
    # Filtre par recherche (client ou chambre)
    if search_query:
        menus = menus.filter(
            Q(client__first_name__icontains=search_query) |
            Q(client__last_name__icontains=search_query) |
            Q(num_chambre__icontains=search_query)
        )
    
    # Filtre par type de repas
    if repas_filter:
        menus = menus.filter(repas=repas_filter)
    
    # Trier par date décroissante
    menus = menus.order_by('-date')
    
    # Appliquer la pagination
    pagination_mixin = PaginationMixin()
    pagination_mixin.paginate_by = 5  # 5 menus par page
    
    queryset_page, paginator = pagination_mixin.paginate_queryset(menus, request)
    pagination_info = pagination_mixin.get_pagination_context(queryset_page, paginator, request)
    
    # Récupérer tous les plats pour le formulaire de modification
    from .models import Plat
    plats = Plat.objects.all().order_by('nom')
    
    # Récupérer tous les patients pour les formulaires
    from apps.patient.models import Patient
    patients = Patient.objects.all().order_by('last_name', 'first_name')
    
    return render(request, 'menu_personnalise.html', {
        'form': form, 
        'menus': queryset_page,
        'pagination_info': pagination_info,
        'plats': plats,
        'patients': patients,
        'search_query': search_query,
        'repas_filter': repas_filter
    })


def menu_personnalise_update(request, pk):
    """Modification d'un menu personnalisé"""
    menu = get_object_or_404(MenuPersonnalise, pk=pk)
    if request.method == 'POST':
        form = MenuPersonnaliseForm(request.POST, instance=menu)
        if form.is_valid():
            menu = form.save()
            messages.success(request, "Le menu personnalisé a été modifié avec succès.")
            return redirect('menu_personnalise_list')
    else:
        form = MenuPersonnaliseForm(instance=menu)
    
    # Récupérer tous les patients pour les formulaires
    from apps.patient.models import Patient
    patients = Patient.objects.all().order_by('last_name', 'first_name')
    
    return render(request, 'menu_personnalise.html', {
        'form': form,
        'patients': patients,
        'action': 'Modifier',
        'title': 'Modifier le Menu Personnalisé'
    })


def menu_personnalise_delete(request, pk):
    """Suppression d'un menu personnalisé"""
    menu = get_object_or_404(MenuPersonnalise, pk=pk)
    if request.method == 'POST':
        menu.delete()
        messages.success(request, "Le menu personnalisé a été supprimé avec succès.")
        return redirect('menu_personnalise_list')
    
    return render(request, 'menu_personnalise_confirm_delete.html', {'menu': menu})


def dashboard_restauration(request):
    """Tableau de bord de la restauration"""
    # Imports nécessaires
    from django.utils import timezone
    from django.db.models import Count, Avg, F
    from datetime import datetime, timedelta, date
    from calendar import monthrange
    from apps.inventory.models import Product, Category, UnitOfMesure
    from apps.hosting.models import Reservation, Companion
    from apps.patient.models import Patient
    
    # Statistiques générales
    total_programmes = Programme.objects.count()
    programmes_actifs = Programme.objects.filter(
        date_debut__lte=timezone.now().date(),
        date_fin__gte=timezone.now().date()
    ).count()
    
    # Nouvelles statistiques pour les programmes
    programmes_termines = Programme.objects.filter(
        date_fin__lt=timezone.now().date()
    ).count()
    
    programmes_a_venir = Programme.objects.filter(
        date_debut__gt=timezone.now().date()
    ).count()
    
    # Durée moyenne des programmes
    programmes_avec_duree = Programme.objects.annotate(
        duree=F('date_fin') - F('date_debut')
    ).filter(duree__isnull=False)
    
    if programmes_avec_duree.exists():
        duree_moyenne = programmes_avec_duree.aggregate(
            avg_duree=Avg('duree')
        )['avg_duree']
        duree_moyenne_jours = duree_moyenne.days if duree_moyenne else 0
    else:
        duree_moyenne_jours = 0
    
    # Statistiques temporelles des programmes
    programmes_ce_mois = Programme.objects.filter(
        date_debut__month=timezone.now().date().month,
        date_debut__year=timezone.now().date().year
    ).count()
    
    programmes_ce_trimestre = Programme.objects.filter(
        date_debut__gte=timezone.now().date().replace(day=1) - timedelta(days=90),
        date_debut__lte=timezone.now().date()
    ).count()
    
    programmes_cette_annee = Programme.objects.filter(
        date_debut__year=timezone.now().date().year
    ).count()
    
    # Répartition des programmes par lieu
    lieux_populaires = Programme.objects.values('lieu').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Répartition des programmes par population
    populations = Programme.objects.values('population').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Top des programmes les plus longs
    programmes_plus_longs = Programme.objects.annotate(
        duree=F('date_fin') - F('date_debut')
    ).filter(duree__isnull=False).order_by('-duree')[:5]
    
    # Top des programmes avec le plus de jours
    programmes_plus_jours = Programme.objects.annotate(
        jours_count=Count('jours')
    ).filter(jours_count__gt=0).order_by('-jours_count')[:5]
    
    # Statistiques des menus de programme
    total_menus_programme = ProgrammeJourMenu.objects.count()
    menus_programme_avec_description = ProgrammeJourMenu.objects.exclude(
        description__isnull=True
    ).exclude(
        description__exact=''
    ).count()
    
    # Répartition des menus de programme par heure de service
    heures_service = ProgrammeJourMenu.objects.values('heure_service').annotate(
        count=Count('id')
    ).order_by('heure_service')
    
    # Plats les plus utilisés dans les programmes
    plats_populaires_programmes = Plat.objects.annotate(
        usage_count=Count('programmejourmenu')
    ).filter(usage_count__gt=0).order_by('-usage_count')[:5]
    
    # Évolution des programmes (6 derniers mois) - données statiques pour l'exemple
    programmes_evolution = [
        {'month': 'Jan', 'actifs': 8, 'termines': 5, 'a_venir': 3},
        {'month': 'Fév', 'actifs': 6, 'termines': 4, 'a_venir': 2},
        {'month': 'Mar', 'actifs': 10, 'termines': 6, 'a_venir': 4},
        {'month': 'Avr', 'actifs': 12, 'termines': 8, 'a_venir': 5},
        {'month': 'Mai', 'actifs': 9, 'termines': 7, 'a_venir': 3},
        {'month': 'Juin', 'actifs': 15, 'termines': 10, 'a_venir': 6}
    ]
    
    total_plats = Plat.objects.count()
    total_menus_standards = MenuStandard.objects.count()
    total_menus_personnalises = MenuPersonnalise.objects.count()
    
    # Statistiques supplémentaires pour les nouveaux onglets
    total_menus_supplementaires = MenuSupplementaire.objects.count()
    
    # Statistiques des ingrédients et catégories
    total_ingredients = Product.objects.filter(active=True).count()
    total_categories = Category.objects.all().count()
    total_unites_mesure = UnitOfMesure.objects.all().count()
    
    # Statistiques pour la section Plats
    total_recettes = Recette.objects.count()
    plats_avec_recette = Plat.objects.filter(recette__isnull=False).count()
    plats_sans_recette = total_plats - plats_avec_recette
    plats_avec_ingredients = LigneRecette.objects.values('recette__plat').distinct().count()
    plats_sans_ingredients = total_plats - plats_avec_ingredients
    
    # Calcul de la moyenne d'ingrédients par plat
    moyenne_ingredients_par_plat = LigneRecette.objects.values('recette__plat').annotate(
        count=Count('id')
    ).aggregate(avg=Avg('count'))['avg'] or 0
    
    # Top 5 plats les plus complexes
    plats_plus_complexes = Plat.objects.annotate(
        ingredient_count=Count('recette__lignes_recette')
    ).filter(ingredient_count__gt=0).order_by('-ingredient_count')[:5]
    
    # Répartition des ingrédients par catégorie
    ingredients_par_categorie = Category.objects.annotate(
        product_count=Count('product')
    ).filter(product_count__gt=0).values('label', 'product_count').order_by('-product_count')
    
    # Top 10 ingrédients par stock pour le graphique
    top_ingredients_stock = Product.objects.filter(
        active=True
    ).order_by('-total_quantity_cached')[:10]
    
    # Statistiques de stock
    stock_faible = Product.objects.filter(
        total_quantity_cached__lte=F('stock_minimal')
    ).count()
    stock_rupture = Product.objects.filter(
        total_quantity_cached=0
    ).count()
    
    # Évolution des plats créés (6 derniers mois)
    # Note: Le modèle Plat n'a pas de champ created_at, on utilise des données statiques pour l'exemple
    plats_par_mois = [
        {'month': 'Jan', 'count': 12},
        {'month': 'Fév', 'count': 19},
        {'month': 'Mar', 'count': 15},
        {'month': 'Avr', 'count': 25},
        {'month': 'Mai', 'count': 22},
        {'month': 'Juin', 'count': 30}
    ]
    
    # Statistiques temporelles des menus
    aujourd_hui = timezone.now().date()
    menus_aujourd_hui = MenuPersonnalise.objects.filter(date=aujourd_hui).count()
    menus_semaine = MenuPersonnalise.objects.filter(
        date__gte=aujourd_hui - timedelta(days=7)
    ).count()
    menus_mois = MenuPersonnalise.objects.filter(
        date__gte=aujourd_hui - timedelta(days=30)
    ).count()
    
    # Statistiques détaillées pour les menus standards
    menus_standards_aujourd_hui = MenuStandard.objects.filter(date=aujourd_hui).count()
    menus_standards_semaine = MenuStandard.objects.filter(
        date__gte=aujourd_hui - timedelta(days=7)
    ).count()
    menus_standards_mois = MenuStandard.objects.filter(
        date__gte=aujourd_hui - timedelta(days=30)
    ).count()
    
    # Répartition des menus standards par type de repas
    repas_choices = MenuStandard.REPAS_CHOICES
    menus_par_repas = {}
    for repas_code, repas_nom in repas_choices:
        count = MenuStandard.objects.filter(repas=repas_code).count()
        menus_par_repas[repas_code] = {
            'nom': repas_nom,
            'count': count
        }
    
    # Répartition des menus personnalisés par type de repas
    menus_personnalises_par_repas = {}
    for repas_code, repas_nom in repas_choices:
        count = MenuPersonnalise.objects.filter(repas=repas_code).count()
        menus_personnalises_par_repas[repas_code] = {
            'nom': repas_nom,
            'count': count
        }
    
    # Répartition des menus supplémentaires par type de repas
    menus_supplementaires_par_repas = {}
    for repas_code, repas_nom in repas_choices:
        count = MenuSupplementaire.objects.filter(repas=repas_code).count()
        menus_supplementaires_par_repas[repas_code] = {
            'nom': repas_nom,
            'count': count
        }
    
    # Top des plats les plus utilisés dans les menus standards
    plats_populaires_standards = Plat.objects.annotate(
        usage_count=Count('menustandard')
    ).filter(usage_count__gt=0).order_by('-usage_count')[:5]
    
    # Statistiques détaillées pour les menus personnalisés
    menus_personnalises_aujourd_hui = MenuPersonnalise.objects.filter(date=aujourd_hui).count()
    menus_personnalises_semaine = MenuPersonnalise.objects.filter(
        date__gte=aujourd_hui - timedelta(days=7)
    ).count()
    menus_personnalises_mois = MenuPersonnalise.objects.filter(
        date__gte=aujourd_hui - timedelta(days=30)
    ).count()
    
    # Répartition des menus personnalisés par type de repas
    menus_personnalises_par_repas = {}
    for repas_code, repas_nom in repas_choices:
        count = MenuPersonnalise.objects.filter(repas=repas_code).count()
        menus_personnalises_par_repas[repas_code] = {
            'nom': repas_nom,
            'count': count
        }
    
    # Top des clients qui commandent le plus
    clients_plus_commandes = Patient.objects.annotate(
        commandes_count=Count('menupersonnalise')
    ).filter(commandes_count__gt=0).order_by('-commandes_count')[:5]
    
    # Répartition des menus personnalisés par chambre
    chambres_plus_commandes = MenuPersonnalise.objects.exclude(
        num_chambre__isnull=True
    ).exclude(
        num_chambre__exact=''
    ).values('num_chambre').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Statistiques détaillées pour les menus supplémentaires
    menus_supplementaires_aujourd_hui = MenuSupplementaire.objects.filter(date=aujourd_hui).count()
    menus_supplementaires_semaine = MenuSupplementaire.objects.filter(
        date__gte=aujourd_hui - timedelta(days=7)
    ).count()
    menus_supplementaires_mois = MenuSupplementaire.objects.filter(
        date__gte=aujourd_hui - timedelta(days=30)
    ).count()
    
    # Répartition des menus supplémentaires par type de repas
    menus_supplementaires_par_repas = {}
    for repas_code, repas_nom in repas_choices:
        count = MenuSupplementaire.objects.filter(repas=repas_code).count()
        menus_supplementaires_par_repas[repas_code] = {
            'nom': repas_nom,
            'count': count
        }
    
    # Top des clients qui demandent le plus de suppléments
    clients_plus_supplements = Patient.objects.annotate(
        supplements_count=Count('menusupplementaire')
    ).filter(supplements_count__gt=0).order_by('-supplements_count')[:5]
    
    # Répartition des menus supplémentaires par chambre
    chambres_plus_supplements = MenuSupplementaire.objects.exclude(
        num_chambre__isnull=True
    ).exclude(
        num_chambre__exact=''
    ).values('num_chambre').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Évolution des menus (6 derniers mois) - données statiques pour l'exemple
    menus_evolution = [
        {'month': 'Jan', 'standards': 45, 'personnalises': 120, 'supplementaires': 30},
        {'month': 'Fév', 'standards': 42, 'personnalises': 115, 'supplementaires': 28},
        {'month': 'Mar', 'standards': 48, 'personnalises': 125, 'supplementaires': 32},
        {'month': 'Avr', 'standards': 50, 'personnalises': 130, 'supplementaires': 35},
        {'month': 'Mai', 'standards': 47, 'personnalises': 128, 'supplementaires': 33},
        {'month': 'Juin', 'standards': 52, 'personnalises': 135, 'supplementaires': 38}
    ]
    
    # Jours sans menu assigné
    jours_sans_menu = ProgrammeJour.objects.filter(menu__isnull=True).count()
    
    # Nombre de clients actuels (avec réservations actives)
    reservations_actives = Reservation.objects.filter(
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    )
    
    if reservations_actives.exists():
        # Compter les clients uniques + leurs accompagnants
        total_personnes = 0
        for reservation in reservations_actives:
            # 1 client par réservation
            total_personnes += 1
            # Ajouter le nombre d'accompagnants pour ce patient
            total_personnes += reservation.patient.companions.count()
        total_personnes_hebergees = total_personnes
    else:
        # Aucune réservation active
        total_personnes_hebergees = 0
    
    # Calendrier hebdomadaire des programmes (lundi au dimanche)
    from datetime import datetime, timedelta
    import calendar
    
    # Navigation dans le calendrier
    today = date.today()
    view_type = request.GET.get('view', 'week')  # week ou month
    date_param = request.GET.get('date', today.strftime('%Y-%m-%d'))
    nav_action = request.GET.get('nav', '')  # prev, next, today
    tab_param = request.GET.get('tab', '')  # tab pour activer un onglet spécifique
    
    try:
        selected_date = datetime.strptime(date_param, '%Y-%m-%d').date()
    except:
        selected_date = today
    
    # Gérer la navigation
    if nav_action == 'prev':
        if view_type == 'week':
            selected_date = selected_date - timedelta(days=7)
        else:
            # Mois précédent
            if selected_date.month == 1:
                selected_date = selected_date.replace(year=selected_date.year - 1, month=12)
            else:
                selected_date = selected_date.replace(month=selected_date.month - 1)
    elif nav_action == 'next':
        if view_type == 'week':
            selected_date = selected_date + timedelta(days=7)
        else:
            # Mois suivant
            if selected_date.month == 12:
                selected_date = selected_date.replace(year=selected_date.year + 1, month=1)
            else:
                selected_date = selected_date.replace(month=selected_date.month + 1)
    elif nav_action == 'today':
        selected_date = today
    
    # Calculer la période à afficher
    if view_type == 'week':
        # Semaine (lundi au dimanche)
        start_of_period = selected_date - timedelta(days=selected_date.weekday())
        end_of_period = start_of_period + timedelta(days=6)
        period_days = 7
    else:
        # Mois
        start_of_period = selected_date.replace(day=1)
        if start_of_period.month == 12:
            end_of_period = start_of_period.replace(year=start_of_period.year + 1, month=1) - timedelta(days=1)
        else:
            end_of_period = start_of_period.replace(month=start_of_period.month + 1) - timedelta(days=1)
        
        # Ajuster pour commencer par lundi de la première semaine
        start_of_period = start_of_period - timedelta(days=start_of_period.weekday())
        period_days = 42  # 6 semaines maximum
    
    # Programmes de la période
    programmes_periode = Programme.objects.filter(
        date_debut__lte=end_of_period,
        date_fin__gte=start_of_period
    ).order_by('date_debut')
    
    
    # Construire le calendrier
    jours_francais = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    calendrier = []
    
    for i in range(period_days):
        jour_date = start_of_period + timedelta(days=i)
        programmes_du_jour = []

        for programme in programmes_periode:
            if programme.date_debut <= jour_date <= programme.date_fin:
                programmes_du_jour.append(programme)

        jour_data = {
            'date': jour_date,
            'nom_jour': jours_francais[jour_date.weekday()],
            'programmes': programmes_du_jour,
            'is_current_month': jour_date.month == selected_date.month,
            'is_today': jour_date == today
        }
        calendrier.append(jour_data)
    
    # Créer les semaines pour la vue mois
    semaines = []
    semaine_courante = []
    for jour_data in calendrier:
        semaine_courante.append(jour_data)
        
        # Créer une nouvelle semaine tous les 7 jours
        if len(semaine_courante) == 7:
            semaines.append(semaine_courante)
            semaine_courante = []
    


    context = {
        'total_programmes': total_programmes,
        'programmes_actifs': programmes_actifs,
        'total_plats': total_plats,
        'total_menus_standards': total_menus_standards,
        'total_menus_personnalises': total_menus_personnalises,
        'total_menus_supplementaires': total_menus_supplementaires,
        'total_ingredients': total_ingredients,
        'total_categories': total_categories,
        'total_unites_mesure': total_unites_mesure,
        'menus_aujourd_hui': menus_aujourd_hui,
        'menus_semaine': menus_semaine,
        'menus_mois': menus_mois,
        'calendrier': calendrier,
        'semaines': semaines,
        'start_of_period': start_of_period,
        'end_of_period': end_of_period,
        'view_type': view_type,
        'selected_date': selected_date,
        'today': today,
        'jours_sans_menu': jours_sans_menu,
        'total_personnes_hebergees': total_personnes_hebergees,
        'reservations_actives': reservations_actives,
        # Nouvelles statistiques pour la section Plats
        'total_recettes': total_recettes,
        'plats_avec_recette': plats_avec_recette,
        'plats_sans_recette': plats_sans_recette,
        'plats_avec_ingredients': plats_avec_ingredients,
        'plats_sans_ingredients': plats_sans_ingredients,
        'moyenne_ingredients_par_plat': moyenne_ingredients_par_plat,
        'plats_plus_complexes': plats_plus_complexes,
        'ingredients_par_categorie': ingredients_par_categorie,
        'top_ingredients_stock': top_ingredients_stock,
        'stock_faible': stock_faible,
        'stock_rupture': stock_rupture,
        'plats_par_mois': plats_par_mois,
        # Nouvelles statistiques pour les menus
        'menus_standards_aujourd_hui': menus_standards_aujourd_hui,
        'menus_standards_semaine': menus_standards_semaine,
        'menus_standards_mois': menus_standards_mois,
        'menus_par_repas': menus_par_repas,
        'plats_populaires_standards': plats_populaires_standards,
        'menus_personnalises_aujourd_hui': menus_personnalises_aujourd_hui,
        'menus_personnalises_semaine': menus_personnalises_semaine,
        'menus_personnalises_mois': menus_personnalises_mois,
        'menus_personnalises_par_repas': menus_personnalises_par_repas,
        'clients_plus_commandes': clients_plus_commandes,
        'chambres_plus_commandes': chambres_plus_commandes,
        'menus_supplementaires_aujourd_hui': menus_supplementaires_aujourd_hui,
        'menus_supplementaires_semaine': menus_supplementaires_semaine,
        'menus_supplementaires_mois': menus_supplementaires_mois,
        'menus_supplementaires_par_repas': menus_supplementaires_par_repas,
        'clients_plus_supplements': clients_plus_supplements,
        'chambres_plus_supplements': chambres_plus_supplements,
        'menus_evolution': menus_evolution,
        'programmes_termines': programmes_termines,
        'programmes_a_venir': programmes_a_venir,
        'duree_moyenne_jours': duree_moyenne_jours,
        'programmes_ce_mois': programmes_ce_mois,
        'programmes_ce_trimestre': programmes_ce_trimestre,
        'programmes_cette_annee': programmes_cette_annee,
        'lieux_populaires': lieux_populaires,
        'populations': populations,
        'programmes_plus_longs': programmes_plus_longs,
        'programmes_plus_jours': programmes_plus_jours,
        'total_menus_programme': total_menus_programme,
        'menus_programme_avec_description': menus_programme_avec_description,
        'heures_service': heures_service,
        'plats_populaires_programmes': plats_populaires_programmes,
        'programmes_evolution': programmes_evolution,
        'tab_param': tab_param,
    }
    return render(request, "dashboard_restauration.html", context)









def api_programmes_mois(request):
    month = int(request.GET.get('mois', date.today().month))
    year = int(request.GET.get('annee', date.today().year))
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])
    programmes = Programme.objects.filter(date_debut__lte=last_day, date_fin__gte=first_day)
    events = []
    for prog in programmes:
        events.append({
            'title': prog.nom,
            'start': str(prog.date_debut),
            'end': str(prog.date_fin),
            'allDay': True,
        })
    return JsonResponse(events, safe=False)

def menu_supplementaire_create(request):
    if request.method == 'POST':
        form = MenuSupplementaireForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('menu_supplementaire_list')
    else:
        form = MenuSupplementaireForm()
    return render(request, 'menu_supplementaire_form.html', {'form': form})

def menu_supplementaire_list(request):
    """Liste des menus supplémentaires avec pagination"""
    from .mixins import PaginationMixin
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            form = MenuSupplementaireForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Menu supplémentaire ajouté avec succès.")
                return redirect('menu_supplementaire_list')
            else:
                messages.error(request, "Erreur lors de l'ajout du menu supplémentaire.")
                
        elif action == 'edit':
            menu_id = request.POST.get('menu_id')
            try:
                menu = MenuSupplementaire.objects.get(id=menu_id)
                form = MenuSupplementaireForm(request.POST, instance=menu)
                if form.is_valid():
                    form.save()
                    return JsonResponse({'success': True, 'message': 'Menu modifié avec succès'})
                else:
                    # Retourner les erreurs de validation détaillées
                    errors = {}
                    for field, field_errors in form.errors.items():
                        errors[field] = [str(error) for error in field_errors]
                    return JsonResponse({
                        'success': False, 
                        'message': 'Données invalides',
                        'errors': errors
                    })
            except MenuSupplementaire.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Menu non trouvé'})
                
        elif action == 'delete':
            menu_id = request.POST.get('menu_id')
            try:
                menu = MenuSupplementaire.objects.get(id=menu_id)
                menu.delete()
                return JsonResponse({'success': True, 'message': 'Menu supprimé avec succès'})
            except MenuSupplementaire.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Menu non trouvé'})
    else:
        form = MenuSupplementaireForm()
    
    # Récupérer les paramètres de filtrage
    search_query = request.GET.get('q', '')
    repas_filter = request.GET.get('repas', '')
    
    # Construire le queryset de base
    menus = MenuSupplementaire.objects.all()
    
    # Filtre par recherche (client ou chambre)
    if search_query:
        menus = menus.filter(
            Q(client__first_name__icontains=search_query) |
            Q(client__last_name__icontains=search_query) |
            Q(num_chambre__icontains=search_query)
        )
    
    # Filtre par type de repas
    if repas_filter:
        menus = menus.filter(repas=repas_filter)
    
    # Trier par date décroissante
    menus = menus.order_by('-date')
    
    # Récupérer tous les patients pour le formulaire de modification
    from apps.patient.models import Patient
    patients = Patient.objects.all().order_by('last_name', 'first_name')
    
    # Appliquer la pagination
    pagination_mixin = PaginationMixin()
    pagination_mixin.paginate_by = 5  # 5 menus par page
    
    queryset_page, paginator = pagination_mixin.paginate_queryset(menus, request)
    pagination_info = pagination_mixin.get_pagination_context(queryset_page, paginator, request)
    
    return render(request, 'menu_supplementaire_list.html', {
        'form': form, 
        'menus': queryset_page,
        'pagination_info': pagination_info,
        'search_query': search_query,
        'repas_filter': repas_filter,
        'patients': patients
    })

def menu_supplementaire_update(request, pk):
    menu = get_object_or_404(MenuSupplementaire, pk=pk)
    if request.method == 'POST':
        form = MenuSupplementaireForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()
            messages.success(request, "Menu supplémentaire modifié avec succès.")
            return redirect('menu_supplementaire_list')
    else:
        form = MenuSupplementaireForm(instance=menu)
    
    return render(request, 'menu_supplementaire_form.html', {'form': form, 'menu': menu})

def menu_supplementaire_delete(request, pk):
    menu = get_object_or_404(MenuSupplementaire, pk=pk)
    if request.method == 'POST':
        menu.delete()
        messages.success(request, "Menu supplémentaire supprimé avec succès.")
        return redirect('menu_supplementaire_list')
    
    return render(request, 'menu_supplementaire_confirm_delete.html', {'menu': menu})

def menu_supplementaire_get_data(request, pk):
    """Vue AJAX pour récupérer les données d'un menu supplémentaire"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            menu = get_object_or_404(MenuSupplementaire, pk=pk)
            data = {
                'id': menu.id,
                'client': str(menu.client) if menu.client else '',
                'num_chambre': menu.num_chambre,
                'date': menu.date.strftime('%Y-%m-%d') if menu.date else '',
                'repas': menu.repas,
                'quantite': menu.quantite,
            }
            return JsonResponse({'success': True, 'data': data})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Requête non AJAX'})

def menu_supplementaire_update_ajax(request, pk):
    """Vue AJAX pour mettre à jour un menu supplémentaire"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            menu = get_object_or_404(MenuSupplementaire, pk=pk)
            
            # Debug: Log des données reçues
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"DEBUG - Données POST reçues: {dict(request.POST)}")
            logger.error(f"DEBUG - Valeur repas reçue: '{request.POST.get('repas')}'")
            logger.error(f"DEBUG - Choix disponibles: {MenuSupplementaire._meta.get_field('repas').choices}")
            
            # Créer une copie mutable des données POST
            post_data = request.POST.copy()
            
            # Le champ client est en lecture seule dans la modale, on garde la valeur existante
            if menu.client:
                post_data['client'] = menu.client.id
            else:
                post_data['client'] = ''
            
            logger.error(f"DEBUG - Données POST modifiées: {dict(post_data)}")
            
            form = MenuSupplementaireForm(post_data, instance=menu)
            if form.is_valid():
                form.save()
                return JsonResponse({'success': True, 'message': 'Menu mis à jour avec succès'})
            else:
                logger.error(f"DEBUG - Erreurs de validation: {form.errors}")
                return JsonResponse({'success': False, 'errors': form.errors})
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"DEBUG - Exception: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Requête non valide'})

def client_suggestions(request):
    query = request.GET.get('q', '')
    if len(query) >= 2:
        clients = Patient.objects.filter(
            models.Q(last_name__icontains=query) | 
            models.Q(first_name__icontains=query)
        )[:10]
        suggestions = [f"{c.first_name} {c.last_name}" for c in clients]
    else:
        suggestions = []
    return JsonResponse({'suggestions': suggestions})

def interventions_list(request):
    """Vue pour lister toutes les demandes d'intervention avec pagination"""
    from .mixins import PaginationMixin
    from apps.demandes.models import DemandeIntervention
    
    # Récupérer toutes les demandes
    demandes = DemandeIntervention.objects.all().order_by('-date_creation')
    
    # Appliquer la pagination
    pagination_mixin = PaginationMixin()
    pagination_mixin.paginate_by = 15  # 15 demandes par page pour cette vue
    
    queryset_page, paginator = pagination_mixin.paginate_queryset(demandes, request)
    pagination_info = pagination_mixin.get_pagination_context(queryset_page, paginator, request)
    
    return render(request, 'interventions_list.html', {
        'demandes': queryset_page,
        'pagination_info': pagination_info
    })


def suivi_consommation_clients(request):
    """Vue pour le suivi de la consommation des clients"""
    from .mixins import PaginationMixin
    
    # Récupérer le terme de recherche
    search_query = request.GET.get('search', '').strip()
    print(f"DEBUG: Terme de recherche reçu: '{search_query}'")
    
    clients_data = []
    
    if search_query:
        print(f"DEBUG: Début de la recherche pour '{search_query}'")
        
        # Recherche plus flexible : diviser les mots de recherche
        mots_recherche = search_query.split()
        print(f"DEBUG: Mots de recherche: {mots_recherche}")
        
        # Rechercher dans les clients avec une logique plus flexible
        clients_trouves = Patient.objects.none()
        for mot in mots_recherche:
            if len(mot) >= 2:  # Ignorer les mots trop courts
                print(f"DEBUG: Recherche du mot '{mot}' dans les clients")
                clients_mot = Patient.objects.filter(
                    Q(last_name__icontains=mot) | Q(first_name__icontains=mot)
                )
                print(f"DEBUG: Clients trouvés pour '{mot}': {clients_mot.count()}")
                for c in clients_mot:
                    print(f"DEBUG:   - {c.first_name} {c.last_name}")
                clients_trouves = clients_trouves | clients_mot
        
        print(f"DEBUG: Total clients trouvés: {clients_trouves.count()}")
        
        # Rechercher aussi dans les accompagnants
        accompagnants_trouves = Companion.objects.none()
        for mot in mots_recherche:
            if len(mot) >= 2:
                print(f"DEBUG: Recherche du mot '{mot}' dans les accompagnants")
                acc_mot = Companion.objects.filter(
                    Q(companion_name__icontains=mot)
                )
                print(f"DEBUG: Accompagnants trouvés pour '{mot}': {acc_mot.count()}")
                for a in acc_mot:
                    print(f"DEBUG:   - {a.companion_name}")
                accompagnants_trouves = accompagnants_trouves | acc_mot
        
        print(f"DEBUG: Total accompagnants trouvés: {accompagnants_trouves.count()}")
        
        # Récupérer toutes les réservations de ces clients (actives et passées)
        reservations_clients = Reservation.objects.filter(
            patient__in=clients_trouves
        ).select_related('patient').prefetch_related('patient__companions', 'room')
        print(f"DEBUG: Réservations trouvées pour les clients: {reservations_clients.count()}")
        
        # Récupérer les réservations où ces accompagnants sont présents
        reservations_accompagnants = Reservation.objects.filter(
            patient__companions__in=accompagnants_trouves
        ).select_related('patient').prefetch_related('patient__companions', 'room')
        print(f"DEBUG: Réservations trouvées pour les accompagnants: {reservations_accompagnants.count()}")
        
        # Combiner et dédupliquer
        toutes_reservations = (reservations_clients | reservations_accompagnants).distinct()
        print(f"DEBUG: Total réservations uniques: {toutes_reservations.count()}")
        
        for res in toutes_reservations:
            print(f"DEBUG: Réservation: {res.patient.first_name} {res.patient.last_name} - {res.start_date} au {res.end_date}")
        
    else:
        print("DEBUG: Pas de recherche, affichage des réservations actives")
        # Si pas de recherche, afficher seulement les réservations actives
        toutes_reservations = Reservation.objects.filter(
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date()
        ).select_related('patient').prefetch_related('patient__companions', 'room')
        print(f"DEBUG: Réservations actives trouvées: {toutes_reservations.count()}")
    
    # Préparer les données pour l'affichage
    print(f"DEBUG: Début de la préparation des données pour {toutes_reservations.count()} réservations")
    for reservation in toutes_reservations:
        print(f"DEBUG: Traitement de la réservation: {reservation.patient.first_name} {reservation.patient.last_name}")
        
        # Recherche plus flexible pour les menus personnalisés
        menus_personnalises = MenuPersonnalise.objects.none()
        mots_pour_menus = mots_recherche if search_query else [reservation.patient.last_name, reservation.patient.first_name]
        for mot in mots_pour_menus:
            if mot and len(mot) >= 2:
                print(f"DEBUG: Recherche de menu personnalisé pour '{mot}'")
                menus_mot = MenuPersonnalise.objects.filter(
                    nom_client__icontains=mot
                ).prefetch_related('plats')
                print(f"DEBUG: Menus personnalisés trouvés pour '{mot}': {menus_mot.count()}")
                menus_personnalises = menus_personnalises | menus_mot
        
        # Recherche plus flexible pour les menus supplémentaires
        menus_supplementaires = MenuSupplementaire.objects.none()
        for mot in mots_pour_menus:
            if mot and len(mot) >= 2:
                print(f"DEBUG: Recherche de menu supplémentaire pour '{mot}'")
                menus_mot = MenuSupplementaire.objects.filter(
                    nom_client__icontains=mot
                )
                print(f"DEBUG: Menus supplémentaires trouvés pour '{mot}': {menus_mot.count()}")
                menus_supplementaires = menus_supplementaires | menus_mot
        
        # Récupérer le numéro de chambre
        chambre_num = reservation.room.room_number if reservation.room else None
        print(f"DEBUG: Chambre trouvée: {chambre_num}")
        
        # Déterminer le statut de la réservation
        aujourd_hui = timezone.now().date()
        if reservation.start_date <= aujourd_hui <= reservation.end_date:
            statut = "active"
        elif reservation.end_date < aujourd_hui:
            statut = "terminée"
        else:
            statut = "future"
        
        # Préparer les données du client
        client_info = {
            'nom_complet': f"{reservation.patient.first_name} {reservation.patient.last_name}",
            'chambre': chambre_num,
            'periode_hebergement': f"{reservation.start_date} au {reservation.end_date}",
            'menus_personnalises': menus_personnalises,
            'menus_supplementaires': menus_supplementaires,
            'reservation': reservation,
            'statut': statut
        }
        
        clients_data.append(client_info)
        print(f"DEBUG: Client ajouté: {client_info['nom_complet']}")
    
    print(f"DEBUG: Total clients_data préparés: {len(clients_data)}")
    
    # Appliquer la pagination
    pagination_mixin = PaginationMixin()
    pagination_mixin.paginate_by = 10  # 10 clients par page
    
    queryset_page, paginator = pagination_mixin.paginate_queryset(clients_data, request)
    pagination_info = pagination_mixin.get_pagination_context(queryset_page, paginator, request)
    
    context = {
        'clients_data': queryset_page,
        'pagination_info': pagination_info,
        'search_query': search_query,
        'total_clients': len(clients_data)
    }
    
    print(f"DEBUG: Contexte final - clients_data: {len(queryset_page)}, total: {len(clients_data)}")
    
    return render(request, 'suivi_consommation_clients.html', context)









def restauration_config(request):
    """Vue de configuration pour la gestion des ingrédients et catégories"""
    from apps.inventory.models import Product, Category, UnitOfMesure
    from apps.patient.models import Patient
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    # Récupérer le paramètre d'onglet
    tab = request.GET.get('tab', 'products')
    
    # Gestion des produits
    if request.method == 'POST' and 'action' in request.POST:
        action = request.POST.get('action')
        
        # Récupérer l'onglet actuel depuis le formulaire
        current_tab = request.POST.get('current_tab', tab)
        
        if action == 'add_product':
            try:
                name = request.POST.get('name')
                default_code = request.POST.get('default_code')
                description = request.POST.get('description')
                standard_price = request.POST.get('standard_price', 0)
                categ_id = request.POST.get('categ')
                uom_id = request.POST.get('uom')
                
                product = Product.objects.create(
                    name=name,
                    default_code=default_code,
                    description=description,
                    standard_price=standard_price,
                    categ_id=categ_id if categ_id else None,
                    uom_id=uom_id if uom_id else None
                )
                messages.success(request, f'Produit "{name}" ajouté avec succès.')
                return redirect(f'{reverse("restauration_config")}?tab={current_tab}')
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'ajout du produit: {str(e)}')
        
        elif action == 'edit_product':
            try:
                product_id = request.POST.get('product_id')
                product = Product.objects.get(product_id=product_id)
                
                product.name = request.POST.get('name')
                product.default_code = request.POST.get('default_code')
                product.description = request.POST.get('description')
                product.standard_price = request.POST.get('standard_price', 0)
                product.categ_id = request.POST.get('categ') if request.POST.get('categ') else None
                product.uom_id = request.POST.get('uom') if request.POST.get('uom') else None
                
                product.save()
                messages.success(request, f'Produit "{product.name}" modifié avec succès.')
                return redirect(f'{reverse("restauration_config")}?tab={current_tab}')
            except Product.DoesNotExist:
                messages.error(request, 'Produit non trouvé.')
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification: {str(e)}')
        
        elif action == 'delete_product':
            try:
                product_id = request.POST.get('product_id')
                product = Product.objects.get(product_id=product_id)
                name = product.name
                product.delete()
                messages.success(request, f'Produit "{name}" supprimé avec succès.')
                return redirect(f'{reverse("restauration_config")}?tab={current_tab}')
            except Product.DoesNotExist:
                messages.error(request, 'Produit non trouvé.')
        
        elif action == 'add_category':
            try:
                label = request.POST.get('name')
                description = request.POST.get('description')
                
                category = Category.objects.create(
                    label=label,
                    description=description
                )
                messages.success(request, f'Catégorie "{label}" ajoutée avec succès.')
                return redirect(f'{reverse("restauration_config")}?tab={current_tab}')
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'ajout de la catégorie: {str(e)}')
        
        elif action == 'edit_category':
            try:
                category_id = request.POST.get('category_id')
                category = Category.objects.get(categ_id=category_id)
                
                category.label = request.POST.get('name')
                category.description = request.POST.get('description')
                
                category.save()
                messages.success(request, f'Catégorie "{category.label}" modifiée avec succès.')
                return redirect(f'{reverse("restauration_config")}?tab={current_tab}')
            except Category.DoesNotExist:
                messages.error(request, 'Catégorie non trouvée.')
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification: {str(e)}')
        
        elif action == 'delete_category':
            try:
                category_id = request.POST.get('category_id')
                category = Category.objects.get(categ_id=category_id)
                label = category.label
                category.delete()
                messages.success(request, f'Catégorie "{label}" supprimée avec succès.')
                return redirect(f'{reverse("restauration_config")}?tab={current_tab}')
            except Category.DoesNotExist:
                messages.error(request, 'Catégorie non trouvée.')
        
        elif action == 'add_uom':
            try:
                label = request.POST.get('name')
                symbole = request.POST.get('symbol')
                
                uom = UnitOfMesure.objects.create(
                    label=label,
                    symbole=symbole
                )
                messages.success(request, f'Unité de mesure "{label}" ajoutée avec succès.')
                return redirect(f'{reverse("restauration_config")}?tab={current_tab}')
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'ajout de l\'unité de mesure: {str(e)}')
        
        elif action == 'edit_uom':
            try:
                uom_id = request.POST.get('uom_id')
                uom = UnitOfMesure.objects.get(uom_id=uom_id)
                
                uom.label = request.POST.get('name')
                uom.symbole = request.POST.get('symbol')
                
                uom.save()
                messages.success(request, f'Unité de mesure "{uom.label}" modifiée avec succès.')
                return redirect(f'{reverse("restauration_config")}?tab={current_tab}')
            except UnitOfMesure.DoesNotExist:
                messages.error(request, 'Unité de mesure non trouvée.')
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification: {str(e)}')
        
        elif action == 'delete_uom':
            try:
                uom_id = request.POST.get('uom_id')
                uom = UnitOfMesure.objects.get(uom_id=uom_id)
                label = uom.label
                uom.delete()
                messages.success(request, f'Unité de mesure "{label}" supprimée avec succès.')
                return redirect(f'{reverse("restauration_config")}?tab={current_tab}')
            except UnitOfMesure.DoesNotExist:
                messages.error(request, 'Unité de mesure non trouvée.')
        
        elif action == 'add_patient':
            try:
                name = request.POST.get('name')
                
                patient = Patient.objects.create(
                    name=name
                )
                messages.success(request, f'Patient "{name}" ajouté avec succès.')
                return redirect(f'{reverse("restauration_config")}?tab={current_tab}')
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'ajout du patient: {str(e)}')
        
        elif action == 'edit_patient':
            try:
                patient_id = request.POST.get('patient_id')
                patient = Patient.objects.get(id=patient_id)
                
                patient.first_name = request.POST.get('first_name', '')
                patient.last_name = request.POST.get('last_name', '')
                
                patient.save()
                messages.success(request, f'Patient "{patient.get_full_name()}" modifié avec succès.')
                return redirect(f'{reverse("restauration_config")}?tab={current_tab}')
            except Patient.DoesNotExist:
                messages.error(request, 'Patient non trouvé.')
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification: {str(e)}')
        
        elif action == 'delete_patient':
            try:
                patient_id = request.POST.get('patient_id')
                patient = Patient.objects.get(id=patient_id)
                name = patient.get_full_name()
                patient.delete()
                messages.success(request, f'Patient "{name}" supprimé avec succès.')
                return redirect(f'{reverse("restauration_config")}?tab={current_tab}')
            except Patient.DoesNotExist:
                messages.error(request, 'Patient non trouvé.')
    
    # Récupération des données avec pagination
    search_query = request.GET.get('q', '')
    
    # Produits
    products = Product.objects.all().order_by('name')
    if search_query and tab == 'products':
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(default_code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Catégories
    categories = Category.objects.all().order_by('label')
    if search_query and tab == 'categories':
        categories = categories.filter(
            Q(label__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Unités de mesure
    uoms = UnitOfMesure.objects.all().order_by('label')
    
    # Patients
    patients = Patient.objects.all().order_by('last_name', 'first_name')
    if search_query and tab == 'patients':
        patients = patients.filter(
            Q(last_name__icontains=search_query) |
            Q(first_name__icontains=search_query)
        )
    
    # Pagination avec PaginationMixin
    from .mixins import PaginationMixin
    
    pagination_mixin = PaginationMixin()
    pagination_mixin.paginate_by = 5  # 5 éléments par page
    
    # Pagination des produits
    products_page, products_paginator = pagination_mixin.paginate_queryset(products, request)
    products_pagination_info = pagination_mixin.get_pagination_context(products_page, products_paginator, request)
    
    # Pagination des catégories
    categories_page, categories_paginator = pagination_mixin.paginate_queryset(categories, request)
    categories_pagination_info = pagination_mixin.get_pagination_context(categories_page, categories_paginator, request)
    
    # Pagination des unités de mesure
    uoms_page, uoms_paginator = pagination_mixin.paginate_queryset(uoms, request)
    uoms_pagination_info = pagination_mixin.get_pagination_context(uoms_page, uoms_paginator, request)
    
    # Pagination des patients
    patients_page, patients_paginator = pagination_mixin.paginate_queryset(patients, request)
    patients_pagination_info = pagination_mixin.get_pagination_context(patients_page, patients_paginator, request)
    
    context = {
        'tab': tab,
        'products': products_page,
        'categories': categories_page,
        'uoms': uoms_page,
        'patients': patients_page,
        'search_query': search_query,
        'products_pagination_info': products_pagination_info,
        'categories_pagination_info': categories_pagination_info,
        'uoms_pagination_info': uoms_pagination_info,
        'patients_pagination_info': patients_pagination_info,
    }
    
    return render(request, 'restauration_config.html', context)








