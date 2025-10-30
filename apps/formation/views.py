from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Q , Avg
from datetime import datetime , timedelta
from .models import Formation, Session, Collaborateur , Inscription , Formateur , Evaluation
from apps.purchases.models import Supplier
from apps.hr.models import Employee 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
import os
from django.conf import settings

def get_status_color(statut):
    """Retourne la couleur selon le statut"""
    colors = {
        'planifiée': '#007bff',    # Bleu
        'en_cours': '#ffc107',     # Jaune
        'terminée': '#28a745',     # Vert
        'annulée': '#dc3545',      # Rouge
    }
    return colors.get(statut, '#6c757d')  # Gris par défaut

from .models import get_type_choices, get_domaine_choices, load_formation_config

def formation_home(request):
    """
    Vue principale pour la gestion des formations
    Gère l'affichage, l'ajout, la modification et la suppression des formations
    """
    
    if request.method == 'POST':
        action = request.POST.get('action', 'add')
        
        if action == 'add':
            # Logique d'ajout de formation
            try:
                # Récupération des données du formulaire
                code = request.POST.get('code')
                titre = request.POST.get('titre')
                description = request.POST.get('description', '')
                type_formation = request.POST.get('type')
                duree_heures = request.POST.get('duree_heures')
                cout = request.POST.get('cout', '')
                domaine = request.POST.get('domaine', '')
                supplier_id = request.POST.get('supplier')
                
                # Validation des champs requis
                if not code or not titre or not type_formation or not duree_heures or not supplier_id:
                    messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
                    return redirect('formation_home')
                
                # Vérification que le code n'existe pas déjà
                if Formation.objects.filter(code=code).exists():
                    messages.error(request, 'Ce code de formation existe déjà.')
                    return redirect('formation_home')
                
                # Validation du type et domaine avec la configuration dynamique
                valid_types = [item['value'] for item in load_formation_config().get('formation_types', [])]
                if type_formation not in valid_types:
                    messages.error(request, 'Type de formation invalide.')
                    return redirect('formation_home')
                
                if domaine:  # Domaine optionnel
                    valid_domaines = [item['value'] for item in load_formation_config().get('formation_domaines', [])]
                    if domaine not in valid_domaines:
                        messages.error(request, 'Domaine de formation invalide.')
                        return redirect('formation_home')
                
                # Validation du supplier
                try:
                    supplier = Supplier.objects.get(id=supplier_id)
                except Supplier.DoesNotExist:
                    messages.error(request, 'Fournisseur introuvable.')
                    return redirect('formation_home')
                
                # Validation de la durée
                try:
                    duree = int(duree_heures)
                    if duree <= 0:
                        messages.error(request, 'La durée doit être supérieure à 0.')
                        return redirect('formation_home')
                except ValueError:
                    messages.error(request, 'Format de durée invalide.')
                    return redirect('formation_home')
                
                # Validation du coût si fourni
                cout_decimal = None
                if cout:
                    try:
                        cout_decimal = float(cout)
                        if cout_decimal < 0:
                            messages.error(request, 'Le coût ne peut pas être négatif.')
                            return redirect('formation_home')
                    except ValueError:
                        messages.error(request, 'Format de coût invalide.')
                        return redirect('formation_home')
                
                # Création de la formation
                formation = Formation.objects.create(
                    code=code,
                    titre=titre,
                    description=description,
                    type=type_formation,
                    duree_heures=duree,
                    cout=cout_decimal,
                    domaine=domaine,
                    supplier=supplier
                )
                
                messages.success(request, f'Formation "{titre}" ajoutée avec succès!')
                return redirect('formation_home')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'ajout de la formation: {str(e)}')
                return redirect('formation_home')
        
        elif action == 'edit':
            # Logique de modification de formation
            try:
                code = request.POST.get('code')
                titre = request.POST.get('titre')
                description = request.POST.get('description', '')
                type_formation = request.POST.get('type')
                duree_heures = request.POST.get('duree_heures')
                cout = request.POST.get('cout', '')
                domaine = request.POST.get('domaine', '')
                supplier_id = request.POST.get('supplier')
                
                # Validation des champs requis
                if not code or not titre or not type_formation or not duree_heures or not supplier_id:
                    messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
                    return redirect('formation_home')
                
                # Récupération de la formation
                try:
                    formation = Formation.objects.get(code=code)
                except Formation.DoesNotExist:
                    messages.error(request, 'Formation introuvable.')
                    return redirect('formation_home')
                
                # Validation du type et domaine avec la configuration dynamique
                valid_types = [item['value'] for item in load_formation_config().get('formation_types', [])]
                if type_formation not in valid_types:
                    messages.error(request, 'Type de formation invalide.')
                    return redirect('formation_home')
                
                if domaine:  # Domaine optionnel
                    valid_domaines = [item['value'] for item in load_formation_config().get('formation_domaines', [])]
                    if domaine not in valid_domaines:
                        messages.error(request, 'Domaine de formation invalide.')
                        return redirect('formation_home')
                
                # Validation du supplier
                try:
                    supplier = Supplier.objects.get(id=supplier_id)
                except Supplier.DoesNotExist:
                    messages.error(request, 'Fournisseur introuvable.')
                    return redirect('formation_home')
                
                # Validation de la durée
                try:
                    duree = int(duree_heures)
                    if duree <= 0:
                        messages.error(request, 'La durée doit être supérieure à 0.')
                        return redirect('formation_home')
                except ValueError:
                    messages.error(request, 'Format de durée invalide.')
                    return redirect('formation_home')
                
                # Validation du coût si fourni
                cout_decimal = None
                if cout:
                    try:
                        cout_decimal = float(cout)
                        if cout_decimal < 0:
                            messages.error(request, 'Le coût ne peut pas être négatif.')
                            return redirect('formation_home')
                    except ValueError:
                        messages.error(request, 'Format de coût invalide.')
                        return redirect('formation_home')
                
                # Mise à jour de la formation
                formation.titre = titre
                formation.description = description
                formation.type = type_formation
                formation.duree_heures = duree
                formation.cout = cout_decimal
                formation.domaine = domaine
                formation.supplier = supplier
                formation.save()
                
                messages.success(request, f'Formation "{titre}" modifiée avec succès!')
                return redirect('formation_home')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification de la formation: {str(e)}')
                return redirect('formation_home')
        
        elif action == 'delete':
            # Logique de suppression de formation
            try:
                code = request.POST.get('code')
                
                if not code:
                    messages.error(request, 'Code de formation manquant.')
                    return redirect('formation_home')
                
                # Récupération et suppression de la formation
                try:
                    formation = Formation.objects.get(code=code)
                    formation_titre = formation.titre
                    formation.delete()
                    messages.success(request, f'Formation "{formation_titre}" supprimée avec succès!')
                except Formation.DoesNotExist:
                    messages.error(request, 'Formation introuvable.')
                
                return redirect('formation_home')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la suppression de la formation: {str(e)}')
                return redirect('formation_home')
    
    # GET request - affichage de la liste
    try:
        query = request.GET.get('q', '').strip()
        
        formations = Formation.objects.select_related('supplier').all()
        if query:
            formations = formations.filter(titre__icontains=query)
        formations = formations.order_by('code')
        
        # Récupération des suppliers pour le formulaire
        suppliers = Supplier.objects.all().order_by('name')
        
        # Récupération des choix dynamiques depuis la configuration
        formation_types = get_type_choices()
        formation_domaines = get_domaine_choices()
        
        context = {
            'formations': formations,
            'suppliers': suppliers,
            'query': query,
            'formation_types': formation_types,  # Choix dynamiques
            'formation_domaines': formation_domaines,  # Choix dynamiques
        }
        
        # Gestion des requêtes AJAX pour la recherche
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html_content = render_to_string('formation/formation_index.html', context)
            # Extraire seulement la partie du tableau
            import re
            table_match = re.search(r'<tbody id="formations-table">(.*?)</tbody>', html_content, re.DOTALL)
            if table_match:
                table_content = table_match.group(1)
                return HttpResponse(table_content)
            else:
                return HttpResponse('<tr><td colspan="7" class="text-center text-danger">Erreur: Impossible de trouver le tableau</td></tr>')
        
        return render(request, 'formation/formation_index.html', context)
        
    except Exception as e:
        print(f"Erreur dans la vue: {str(e)}")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'error': str(e)}, status=500)
        raise

######
# views.py - Vue session_home mise à jour

def session_home(request):
    """
    Vue principale pour la gestion des sessions de formation
    Gère l'affichage, l'ajout, la modification et la suppression des sessions
    """
    
    if request.method == 'POST':
        action = request.POST.get('action', 'add')
        
        if action == 'add':
            # Logique d'ajout de session
            try:
                # Récupération des données du formulaire
                formation_code = request.POST.get('formation')
                formateur_id = request.POST.get('formateur')
                date_debut = request.POST.get('date_debut')
                date_fin = request.POST.get('date_fin')
                lieu = request.POST.get('lieu', '')
                places_totales = request.POST.get('places_totales')
                statut = request.POST.get('statut', 'planifiée')
                
                # Validation des champs requis
                if not formation_code or not formateur_id or not date_debut or not date_fin or not places_totales:
                    messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
                    return redirect('session_home')
                
                # Validation de la formation
                try:
                    formation = Formation.objects.get(code=formation_code)
                except Formation.DoesNotExist:
                    messages.error(request, 'Formation introuvable.')
                    return redirect('session_home')
                
                # Validation du formateur
                try:
                    formateur = Formateur.objects.get(id=formateur_id)
                except Formateur.DoesNotExist:
                    messages.error(request, 'Formateur introuvable.')
                    return redirect('session_home')
                
                # Validation du nombre de places
                try:
                    places = int(places_totales)
                    if places <= 0:
                        messages.error(request, 'Le nombre de places doit être supérieur à 0.')
                        return redirect('session_home')
                except ValueError:
                    messages.error(request, 'Format du nombre de places invalide.')
                    return redirect('session_home')
                
                # Validation des dates
                try:
                    date_debut_dt = datetime.strptime(date_debut, '%Y-%m-%dT%H:%M')
                    date_fin_dt = datetime.strptime(date_fin, '%Y-%m-%dT%H:%M')
                    
                    if date_debut_dt >= date_fin_dt:
                        messages.error(request, 'La date de fin doit être postérieure à la date de début.')
                        return redirect('session_home')
                    
                    # Convertir en timezone aware
                    date_debut_dt = timezone.make_aware(date_debut_dt)
                    date_fin_dt = timezone.make_aware(date_fin_dt)
                    
                except ValueError:
                    messages.error(request, 'Format de date invalide.')
                    return redirect('session_home')
                
                # Vérifier les conflits d'horaires du formateur
                conflits = Session.objects.filter(
                    formateur=formateur,
                    statut__in=['planifiée', 'en_cours']
                ).filter(
                    Q(date_debut__lte=date_fin_dt, date_fin__gte=date_debut_dt)
                )
                
                if conflits.exists():
                    messages.error(request, f'Le formateur {formateur} a déjà une session programmée à ces dates.')
                    return redirect('session_home')
                
                # Création de la session
                session = Session.objects.create(
                    formation=formation,
                    formateur=formateur,
                    date_debut=date_debut_dt,
                    date_fin=date_fin_dt,
                    lieu=lieu,
                    places_totales=places,
                    statut=statut
                )
                
                messages.success(request, f'Session "{formation.titre}" créée avec succès!')
                return redirect('session_home')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la création de la session: {str(e)}')
                return redirect('session_home')
        
        elif action == 'edit':
            # Logique de modification de session
            try:
                session_id = request.POST.get('session_id')
                formation_code = request.POST.get('formation')
                formateur_id = request.POST.get('formateur')
                date_debut = request.POST.get('date_debut')
                date_fin = request.POST.get('date_fin')
                lieu = request.POST.get('lieu', '')
                places_totales = request.POST.get('places_totales')
                statut = request.POST.get('statut')
                
                # Validation des champs requis
                if not session_id or not formation_code or not formateur_id or not date_debut or not date_fin or not places_totales:
                    messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
                    return redirect('session_home')
                
                # Récupération de la session
                try:
                    session = Session.objects.get(id=session_id)
                except Session.DoesNotExist:
                    messages.error(request, 'Session introuvable.')
                    return redirect('session_home')
                
                # Validation de la formation
                try:
                    formation = Formation.objects.get(code=formation_code)
                except Formation.DoesNotExist:
                    messages.error(request, 'Formation introuvable.')
                    return redirect('session_home')
                
                # Validation du formateur
                try:
                    formateur = Formateur.objects.get(id=formateur_id)
                except Formateur.DoesNotExist:
                    messages.error(request, 'Formateur introuvable.')
                    return redirect('session_home')
                
                # Validation du nombre de places
                try:
                    places = int(places_totales)
                    if places <= 0:
                        messages.error(request, 'Le nombre de places doit être supérieur à 0.')
                        return redirect('session_home')
                except ValueError:
                    messages.error(request, 'Format du nombre de places invalide.')
                    return redirect('session_home')
                
                # Validation des dates
                try:
                    date_debut_dt = datetime.strptime(date_debut, '%Y-%m-%dT%H:%M')
                    date_fin_dt = datetime.strptime(date_fin, '%Y-%m-%dT%H:%M')
                    
                    if date_debut_dt >= date_fin_dt:
                        messages.error(request, 'La date de fin doit être postérieure à la date de début.')
                        return redirect('session_home')
                    
                    # Convertir en timezone aware
                    date_debut_dt = timezone.make_aware(date_debut_dt)
                    date_fin_dt = timezone.make_aware(date_fin_dt)
                    
                except ValueError:
                    messages.error(request, 'Format de date invalide.')
                    return redirect('session_home')
                
                # Vérifier les conflits d'horaires du formateur (exclure la session actuelle)
                conflits = Session.objects.filter(
                    formateur=formateur,
                    statut__in=['planifiée', 'en_cours']
                ).exclude(id=session_id).filter(
                    Q(date_debut__lte=date_fin_dt, date_fin__gte=date_debut_dt)
                )
                
                if conflits.exists():
                    messages.error(request, f'Le formateur {formateur} a déjà une session programmée à ces dates.')
                    return redirect('session_home')
                
                # Mise à jour de la session
                session.formation = formation
                session.formateur = formateur
                session.date_debut = date_debut_dt
                session.date_fin = date_fin_dt
                session.lieu = lieu
                session.places_totales = places
                session.statut = statut
                session.save()
                
                messages.success(request, f'Session "{formation.titre}" modifiée avec succès!')
                return redirect('session_home')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification de la session: {str(e)}')
                return redirect('session_home')
        
        elif action == 'delete':
            # Logique de suppression de session
            try:
                session_id = request.POST.get('session_id')
                
                if not session_id:
                    messages.error(request, 'ID de session manquant.')
                    return redirect('session_home')
                
                # Récupération et suppression de la session
                try:
                    session = Session.objects.get(id=session_id)
                    session_titre = f"{session.formation.titre} - {session.date_debut.strftime('%Y-%m-%d')}"
                    
                    # Vérifier s'il y a des inscriptions
                    inscriptions_count = session.inscription_set.count()
                    if inscriptions_count > 0:
                        messages.error(request, f'Impossible de supprimer cette session car elle contient {inscriptions_count} inscription(s).')
                        return redirect('session_home')
                    
                    session.delete()
                    messages.success(request, f'Session "{session_titre}" supprimée avec succès!')
                except Session.DoesNotExist:
                    messages.error(request, 'Session introuvable.')
                
                return redirect('session_home')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la suppression de la session: {str(e)}')
                return redirect('session_home')
    
    # GET request - affichage de la liste
    try:
        # Filtres
        formation_filter = request.GET.get('formation', '').strip()
        statut_filter = request.GET.get('statut', '').strip()
        formateur_filter = request.GET.get('formateur', '').strip()
        date_debut_filter = request.GET.get('date_debut', '').strip()
        
        # Requête de base avec annotations
        sessions = Session.objects.select_related('formation', 'formateur').annotate(
            inscriptions_count=Count('inscription')
        ).all()
        
        # Application des filtres
        if formation_filter:
            sessions = sessions.filter(formation__titre__icontains=formation_filter)
        if statut_filter:
            sessions = sessions.filter(statut=statut_filter)
        if formateur_filter:
            sessions = sessions.filter(formateur__nom__icontains=formateur_filter)
        if date_debut_filter:
            sessions = sessions.filter(date_debut__date=date_debut_filter)
        
        sessions = sessions.order_by('-date_debut')
        
        # Récupération des données pour les formulaires
        formations = Formation.objects.all().order_by('titre')
        formateurs = Formateur.objects.all().order_by('nom', 'prenom')  # Changé de collaborateurs à formateurs
        
        context = {
            'sessions': sessions,
            'formations': formations,
            'formateurs': formateurs,  # Changé de collaborateurs à formateurs
            'session_statuts': Session.STATUT_CHOICES,
            'formation_filter': formation_filter,
            'statut_filter': statut_filter,
            'formateur_filter': formateur_filter,
            'date_debut_filter': date_debut_filter,
        }
        
        # Gestion des requêtes AJAX pour les filtres
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html_content = render_to_string('formation/session_index.html', context)
            # Extraire seulement la partie du tableau
            import re
            table_match = re.search(r'<tbody id="sessions-table">(.*?)</tbody>', html_content, re.DOTALL)
            if table_match:
                table_content = table_match.group(1)
                return HttpResponse(table_content)
            else:
                return HttpResponse('<tr><td colspan="8" class="text-center text-danger">Erreur: Impossible de trouver le tableau</td></tr>')
        
        return render(request, 'formation/session_index.html', context)
        
    except Exception as e:
        print(f"Erreur dans la vue session: {str(e)}")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=500)
        raise
  
#####

def inscription_home(request):
    """
    Vue principale pour la gestion des inscriptions
    Gère l'affichage, l'ajout, la modification et la suppression des inscriptions
    Utilise Employee au lieu de Collaborateur
    """
    
    if request.method == 'POST':
        action = request.POST.get('action', 'add')
        
        if action == 'add':
            # Logique d'ajout d'inscription
            try:
                # Récupération des données du formulaire
                session_id = request.POST.get('session')
                employee_id = request.POST.get('employee')
                statut = request.POST.get('statut', 'inscrit')
                
                # Validation des champs requis
                if not session_id or not employee_id:
                    messages.error(request, 'Veuillez sélectionner une session et un employé.')
                    return redirect('inscription_home')
                
                # Validation de la session
                try:
                    session = Session.objects.get(id=session_id)
                except Session.DoesNotExist:
                    messages.error(request, 'Session introuvable.')
                    return redirect('inscription_home')
                
                # Validation de l'employé
                try:
                    employee = Employee.objects.get(id=employee_id)  # ← Plus besoin d'importation locale
                except Employee.DoesNotExist:
                    messages.error(request, 'Employé introuvable.')
                    return redirect('inscription_home')
                
                # Vérifier si l'employé n'est pas déjà inscrit
                if Inscription.objects.filter(session=session, employee=employee).exists():
                    messages.error(request, f'{employee.full_name} est déjà inscrit à cette session.')
                    return redirect('inscription_home')
                
                # Vérifier les places disponibles
                inscriptions_count = session.inscription_set.count()
                if inscriptions_count >= session.places_totales:
                    messages.error(request, 'Cette session est complète.')
                    return redirect('inscription_home')
                
                # Vérifier que la session est dans un état permettant l'inscription
                if session.statut not in ['planifiée', 'en_cours']:
                    messages.error(request, 'Impossible de s\'inscrire à cette session.')
                    return redirect('inscription_home')
                
                # Création de l'inscription
                inscription = Inscription.objects.create(
                    session=session,
                    employee=employee,
                    statut=statut
                )
                
                messages.success(request, f'Inscription de {employee.full_name} à la session "{session.formation.titre}" créée avec succès!')
                return redirect('inscription_home')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la création de l\'inscription: {str(e)}')
                return redirect('inscription_home')
        
        elif action == 'edit':
            # Logique de modification d'inscription
            try:
                inscription_id = request.POST.get('inscription_id')
                session_id = request.POST.get('session')
                employee_id = request.POST.get('employee')
                statut = request.POST.get('statut')
                
                # Validation des champs requis
                if not inscription_id or not session_id or not employee_id or not statut:
                    messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
                    return redirect('inscription_home')
                
                # Récupération de l'inscription
                try:
                    inscription = Inscription.objects.get(id=inscription_id)
                except Inscription.DoesNotExist:
                    messages.error(request, 'Inscription introuvable.')
                    return redirect('inscription_home')
                
                # Validation de la session
                try:
                    session = Session.objects.get(id=session_id)
                except Session.DoesNotExist:
                    messages.error(request, 'Session introuvable.')
                    return redirect('inscription_home')
                
                # Validation de l'employé
                try:
                    # ← SUPPRIMEZ cette ligne : from recruitment.models import Employee
                    employee = Employee.objects.get(id=employee_id)
                except Employee.DoesNotExist:
                    messages.error(request, 'Employé introuvable.')
                    return redirect('inscription_home')
                
                # Vérifier si l'employé n'est pas déjà inscrit à cette session (exclure l'inscription actuelle)
                if Inscription.objects.filter(session=session, employee=employee).exclude(id=inscription_id).exists():
                    messages.error(request, f'{employee.full_name} est déjà inscrit à cette session.')
                    return redirect('inscription_home')
                
                # Mise à jour de l'inscription
                inscription.session = session
                inscription.employee = employee
                inscription.statut = statut
                inscription.save()
                
                messages.success(request, f'Inscription de {employee.full_name} modifiée avec succès!')
                return redirect('inscription_home')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification de l\'inscription: {str(e)}')
                return redirect('inscription_home')
        
        elif action == 'delete':
            # Logique de suppression d'inscription
            try:
                inscription_id = request.POST.get('inscription_id')
                
                if not inscription_id:
                    messages.error(request, 'ID d\'inscription manquant.')
                    return redirect('inscription_home')
                
                # Récupération et suppression de l'inscription
                try:
                    inscription = Inscription.objects.get(id=inscription_id)
                    employee_nom = inscription.employee.full_name
                    session_titre = inscription.session.formation.titre
                    
                    inscription.delete()
                    messages.success(request, f'Inscription de {employee_nom} à "{session_titre}" supprimée avec succès!')
                except Inscription.DoesNotExist:
                    messages.error(request, 'Inscription introuvable.')
                
                return redirect('inscription_home')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la suppression de l\'inscription: {str(e)}')
                return redirect('inscription_home')
        
        elif action == 'bulk_presence':
            # Logique pour marquer la présence en masse
            try:
                session_id = request.POST.get('session_id')
                inscription_ids = request.POST.getlist('inscription_ids[]')
                
                if not session_id or not inscription_ids:
                    messages.error(request, 'Données manquantes pour la gestion des présences.')
                    return redirect('inscription_home')
                
                # Mettre à jour les présences
                updated_count = Inscription.objects.filter(
                    id__in=inscription_ids,
                    session_id=session_id
                ).update(statut='present')
                
                messages.success(request, f'{updated_count} présence(s) mise(s) à jour avec succès!')
                return redirect('inscription_home')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la mise à jour des présences: {str(e)}')
                return redirect('inscription_home')
    
    # GET request - affichage de la liste
    try: 
        # Filtres
        session_filter = request.GET.get('session', '').strip()
        employee_filter = request.GET.get('employee', '').strip()
        statut_filter = request.GET.get('statut', '').strip()
        formation_filter = request.GET.get('formation', '').strip()
        
        # Requête de base avec joins
        inscriptions = Inscription.objects.select_related(
            'session',
            'session__formation',
            'session__formateur',
            'employee'  
        ).all()
        
        # Application des filtres
        if session_filter:
            inscriptions = inscriptions.filter(session__id=session_filter)
        if employee_filter:
            inscriptions = inscriptions.filter(employee__id=employee_filter)
        if statut_filter:
            inscriptions = inscriptions.filter(statut=statut_filter)
        if formation_filter:
            inscriptions = inscriptions.filter(session__formation__code=formation_filter)
        
        inscriptions = inscriptions.order_by('-date_inscription')
        
        # Récupération des données pour les formulaires
        sessions = Session.objects.select_related('formation', 'formateur').filter(
            statut__in=['planifiée', 'en_cours']
        ).order_by('-date_debut')
        
        # Tous les employés pour les filtres
        all_employees = Employee.objects.filter(status='A').order_by('full_name')
        
        # Employés actifs pour les nouvelles inscriptions
        active_employees = Employee.objects.filter(
            status='A'
        ).order_by('full_name')
        
        # Gestion de la pagination
        paginator = Paginator(inscriptions, 20)
        page_number = request.GET.get('page', 1)
        try:
            page_obj = paginator.get_page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.get_page(1)
        except EmptyPage:
            page_obj = paginator.get_page(paginator.num_pages)
        
        # Statistiques
        stats = {
            'total_inscriptions': inscriptions.count(),
            'inscrits': inscriptions.filter(statut='inscrit').count(),
            'presents': inscriptions.filter(statut='present').count(),
            'absents': inscriptions.filter(statut='absent').count(),
        }
        
        context = {
            'page_obj': page_obj,
            'inscriptions': inscriptions,
            'sessions': sessions,
            'all_employees': all_employees,
            'active_employees': active_employees,
            'formations': Formation.objects.all(),
            'inscription_statuts': Inscription.STATUT_CHOICES,
            'session_filter': session_filter,
            'employee_filter': employee_filter,
            'statut_filter': statut_filter,
            'formation_filter': formation_filter,
            'stats': stats,
        }
        
        # Gestion des requêtes AJAX pour les filtres
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html_content = render_to_string('formation/inscription_index.html', context)


            import re
            table_match = re.search(r'<tbody id="inscriptions-table">(.*?)</tbody>', html_content, re.DOTALL)
            if table_match:
                table_content = table_match.group(1)
                return HttpResponse(table_content)
            else:
                return HttpResponse('<tr><td colspan="7" class="text-center text-danger">Erreur: Impossible de trouver le tableau</td></tr>')
        
        return render(request, 'formation/inscription_index.html', context)
        
    except Exception as e:
        print(f"Erreur dans la vue inscription: {str(e)}")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=500)
        raise
#######
def formateur_home(request):
    """
    Vue principale pour la gestion des formateurs
    Gère l'affichage, l'ajout, la modification et la suppression des formateurs
    """
    
    if request.method == 'POST':
        action = request.POST.get('action', 'add')
        
        if action == 'add':
            # Logique d'ajout de formateur
            try:
                # Récupération des données du formulaire
                nom = request.POST.get('nom', '').strip()
                prenom = request.POST.get('prenom', '').strip()
                service = request.POST.get('service', '').strip()
                
                # Validation des champs requis
                if not nom or not prenom or not service:
                    messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
                    return redirect('formateur_home')
                
                # Vérifier si le formateur existe déjà
                formateur_exists = Formateur.objects.filter(
                    nom__iexact=nom,
                    prenom__iexact=prenom
                ).exists()
                
                if formateur_exists:
                    messages.error(request, f'Le formateur {prenom} {nom} existe déjà.')
                    return redirect('formateur_home')
                
                # Création du formateur
                formateur = Formateur.objects.create(
                    nom=nom,
                    prenom=prenom,
                    service=service
                )
                
                messages.success(request, f'Formateur "{prenom} {nom}" créé avec succès!')
                return redirect('formateur_home')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la création du formateur: {str(e)}')
                return redirect('formateur_home')
        
        elif action == 'edit':
            # Logique de modification de formateur
            try:
                formateur_id = request.POST.get('formateur_id')
                nom = request.POST.get('nom', '').strip()
                prenom = request.POST.get('prenom', '').strip()
                service = request.POST.get('service', '').strip()
                
                # Validation des champs requis
                if not formateur_id or not nom or not prenom or not service:
                    messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
                    return redirect('formateur_home')
                
                # Récupération du formateur
                try:
                    formateur = Formateur.objects.get(id=formateur_id)
                except Formateur.DoesNotExist:
                    messages.error(request, 'Formateur introuvable.')
                    return redirect('formateur_home')
                
                # Vérifier si un autre formateur avec le même nom/prénom existe
                formateur_exists = Formateur.objects.filter(
                    nom__iexact=nom,
                    prenom__iexact=prenom
                ).exclude(id=formateur_id).exists()
                
                if formateur_exists:
                    messages.error(request, f'Un autre formateur avec le nom {prenom} {nom} existe déjà.')
                    return redirect('formateur_home')
                
                # Mise à jour du formateur
                formateur.nom = nom
                formateur.prenom = prenom
                formateur.service = service
                formateur.save()
                
                messages.success(request, f'Formateur "{prenom} {nom}" modifié avec succès!')
                return redirect('formateur_home')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification du formateur: {str(e)}')
                return redirect('formateur_home')
        
        elif action == 'delete':
            # Logique de suppression de formateur
            try:
                formateur_id = request.POST.get('formateur_id')
                
                if not formateur_id:
                    messages.error(request, 'ID de formateur manquant.')
                    return redirect('formateur_home')
                
                # Récupération et suppression du formateur
                try:
                    formateur = Formateur.objects.get(id=formateur_id)
                    formateur_nom = f"{formateur.prenom} {formateur.nom}"
                    
                    # Vérifier s'il y a des sessions associées
                    sessions_count = Session.objects.filter(formateur=formateur).count()
                    if sessions_count > 0:
                        messages.error(request, f'Impossible de supprimer ce formateur car il est associé à {sessions_count} session(s).')
                        return redirect('formateur_home')
                    
                    formateur.delete()
                    messages.success(request, f'Formateur "{formateur_nom}" supprimé avec succès!')
                except Formateur.DoesNotExist:
                    messages.error(request, 'Formateur introuvable.')
                
                return redirect('formateur_home')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la suppression du formateur: {str(e)}')
                return redirect('formateur_home')
    
    # GET request - affichage de la liste
    try:
        # Filtres
        nom_filter = request.GET.get('nom', '').strip()
        
        # Requête de base - tous les formateurs avec compteurs de sessions
        formateurs = Formateur.objects.annotate(
            sessions_count=Count('session', filter=Q(session__isnull=False)),
            sessions_actives_count=Count('session', filter=Q(session__statut__in=['planifiée', 'en_cours']))
        )
        
        # Application du filtre par nom
        if nom_filter:
            formateurs = formateurs.filter(
                Q(nom__icontains=nom_filter) | Q(prenom__icontains=nom_filter)
            )
        
        formateurs = formateurs.order_by('nom', 'prenom')
        
        # Gestion des requêtes AJAX pour le filtre de recherche
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Rendu du contenu du tableau uniquement
            table_rows = ""
            if formateurs.exists():
                for formateur in formateurs:
                    table_rows += f"""
                    <tr>
                        <td>{formateur.nom}</td>
                        <td>{formateur.prenom}</td>
                        <td><span class="badge bg-secondary">{formateur.service}</span></td>
                        <td><span class="badge bg-info">{formateur.sessions_count or 0}</span></td>
                        <td><span class="badge bg-{'success' if formateur.sessions_actives_count and formateur.sessions_actives_count > 0 else 'secondary'}">{formateur.sessions_actives_count or 0}</span></td>
                        <td>
                            <div class="btn-group" role="group">
                                <button class="btn btn-sm btn-outline-primary" 
                                        data-bs-toggle="modal" 
                                        data-bs-target="#modalEditFormateur" 
                                        data-formateur-id="{formateur.id}"
                                        data-formateur-nom="{formateur.nom}"
                                        data-formateur-prenom="{formateur.prenom}"
                                        data-formateur-service="{formateur.service}"
                                        title="Modifier ce formateur">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger" 
                                        data-bs-toggle="modal" 
                                        data-bs-target="#modalDeleteFormateur"
                                        data-formateur-id="{formateur.id}" 
                                        data-formateur-nom="{formateur.prenom} {formateur.nom}"
                                        title="Supprimer ce formateur">
                                    <i class="fas fa-trash-alt"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                    """
            else:
                table_rows = '<tr><td colspan="6" class="text-center">Aucun formateur trouvé</td></tr>'
            
            return HttpResponse(table_rows)
        
        # Rendu normal de la page
        context = {
            'formateurs': formateurs,
            'nom_filter': nom_filter,
        }
        
        return render(request, 'formation/formateur_index.html', context)
        
    except Exception as e:
        print(f"Erreur dans la vue formateur: {str(e)}")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponse('<tr><td colspan="6" class="text-center text-danger">Erreur lors de la recherche</td></tr>')
        
        messages.error(request, f'Erreur lors du chargement des formateurs: {str(e)}')
        return render(request, 'formation/formateur_index.html', {'formateurs': Formateur.objects.none()})
    
    #############
def cours_programmes_home(request):
    """
    Vue principale pour la gestion des cours et programmes
    Gère l'affichage des sessions, le calendrier, et les fonctionnalités PDF
    """
    from django.shortcuts import render, redirect, get_object_or_404
    from django.contrib import messages
    from django.http import HttpResponse, JsonResponse
    from django.template.loader import render_to_string
    from django.db.models import Q, Count
    from django.utils import timezone
    from datetime import datetime, timedelta
    import json
    from .models import Session, Formation, Formateur, Inscription
    from apps.hr.models import Employee
    
    # Import pour PDF
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.units import inch
    from io import BytesIO
    
    if request.method == 'POST':
        action = request.POST.get('action', 'add')
        
        if action == 'add_session':
            # Logique d'ajout de session
            try:
                formation_code = request.POST.get('formation')
                formateur_id = request.POST.get('formateur')
                date_debut = request.POST.get('date_debut')
                date_fin = request.POST.get('date_fin')
                lieu = request.POST.get('lieu', '')
                places_totales = request.POST.get('places_totales')
                statut = request.POST.get('statut', 'planifiée')
                
                # Validation des champs requis
                if not formation_code or not formateur_id or not date_debut or not date_fin or not places_totales:
                    messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
                    return redirect('cours_programmes_home')
                
                # Validation de la formation
                try:
                    formation = Formation.objects.get(code=formation_code)
                except Formation.DoesNotExist:
                    messages.error(request, 'Formation introuvable.')
                    return redirect('cours_programmes_home')
                
                # Validation du formateur
                try:
                    formateur = Formateur.objects.get(id=formateur_id)
                except Formateur.DoesNotExist:
                    messages.error(request, 'Formateur introuvable.')
                    return redirect('cours_programmes_home')
                
                # Validation des dates - CORRECTION: utiliser timezone.datetime au lieu du module datetime
                try:
                    # Ajout du timezone pour être cohérent avec Django
                    from django.utils.dateparse import parse_datetime
                    
                    date_debut_obj = parse_datetime(date_debut.replace('T', ' '))
                    date_fin_obj = parse_datetime(date_fin.replace('T', ' '))
                    
                    # Si pas de timezone, on utilise le timezone par défaut
                    if date_debut_obj.tzinfo is None:
                        date_debut_obj = timezone.make_aware(date_debut_obj)
                    if date_fin_obj.tzinfo is None:
                        date_fin_obj = timezone.make_aware(date_fin_obj)
                    
                    if date_debut_obj >= date_fin_obj:
                        messages.error(request, 'La date de fin doit être postérieure à la date de début.')
                        return redirect('cours_programmes_home')
                        
                    if date_debut_obj < timezone.now():
                        messages.error(request, 'La date de début ne peut pas être dans le passé.')
                        return redirect('cours_programmes_home')
                        
                except (ValueError, TypeError):
                    messages.error(request, 'Format de date invalide.')
                    return redirect('cours_programmes_home')
                
                # Validation du nombre de places
                try:
                    places = int(places_totales)
                    if places <= 0:
                        messages.error(request, 'Le nombre de places doit être supérieur à 0.')
                        return redirect('cours_programmes_home')
                except ValueError:
                    messages.error(request, 'Nombre de places invalide.')
                    return redirect('cours_programmes_home')
                
                # Création de la session
                session = Session.objects.create(
                    formation=formation,
                    formateur=formateur,
                    date_debut=date_debut_obj,
                    date_fin=date_fin_obj,
                    lieu=lieu,
                    places_totales=places,
                    statut=statut
                )
                
                messages.success(request, f'Session "{formation.titre}" programmée avec succès!')
                return redirect('cours_programmes_home')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la création de la session: {str(e)}')
                return redirect('cours_programmes_home')
        
        elif action == 'edit_session':
            # Logique de modification de session
            try:
                session_id = request.POST.get('session_id')
                formation_code = request.POST.get('formation')
                formateur_id = request.POST.get('formateur')
                date_debut = request.POST.get('date_debut')
                date_fin = request.POST.get('date_fin')
                lieu = request.POST.get('lieu', '')
                places_totales = request.POST.get('places_totales')
                statut = request.POST.get('statut')
                
                # Récupération de la session
                try:
                    session = Session.objects.get(id=session_id)
                except Session.DoesNotExist:
                    messages.error(request, 'Session introuvable.')
                    return redirect('cours_programmes_home')
                
                # Validations similaires à l'ajout
                formation = get_object_or_404(Formation, code=formation_code)
                formateur = get_object_or_404(Formateur, id=formateur_id)
                
                # CORRECTION: même logique de validation des dates
                from django.utils.dateparse import parse_datetime
                
                date_debut_obj = parse_datetime(date_debut.replace('T', ' '))
                date_fin_obj = parse_datetime(date_fin.replace('T', ' '))
                
                if date_debut_obj.tzinfo is None:
                    date_debut_obj = timezone.make_aware(date_debut_obj)
                if date_fin_obj.tzinfo is None:
                    date_fin_obj = timezone.make_aware(date_fin_obj)
                
                places = int(places_totales)
                
                # Mise à jour de la session
                session.formation = formation
                session.formateur = formateur
                session.date_debut = date_debut_obj
                session.date_fin = date_fin_obj
                session.lieu = lieu
                session.places_totales = places
                session.statut = statut
                session.save()
                
                messages.success(request, 'Session modifiée avec succès!')
                return redirect('cours_programmes_home')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification: {str(e)}')
                return redirect('cours_programmes_home')
        
        elif action == 'delete_session':
            # Logique de suppression de session
            try:
                session_id = request.POST.get('session_id')
                session = get_object_or_404(Session, id=session_id)
                
                session_titre = f"{session.formation.titre} - {session.date_debut.strftime('%Y-%m-%d')}"
                session.delete()
                messages.success(request, f'Session "{session_titre}" supprimée avec succès!')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la suppression: {str(e)}')
            
            return redirect('cours_programmes_home')
        
        elif action == 'inscriptions':
            # Gestion des inscriptions
            try:
                session_id = request.POST.get('session_id')
                employee_ids = request.POST.getlist('employees')
                
                session = get_object_or_404(Session, id=session_id)
                
                # Vérifier la capacité
                inscriptions_actuelles = Inscription.objects.filter(
                    session=session, 
                    statut__in=['inscrit', 'present']
                ).count()
                
                if inscriptions_actuelles + len(employee_ids) > session.places_totales:
                    messages.error(request, 'Nombre de places insuffisant.')
                    return redirect('cours_programmes_home')
                
                # Créer les inscriptions
                inscriptions_creees = 0
                for employee_id in employee_ids:
                    try:
                        employee = get_object_or_404(Employee, id=employee_id)
                        inscription, created = Inscription.objects.get_or_create(
                            session=session,
                            employee=employee,
                            defaults={'statut': 'inscrit'}
                        )
                        if created:
                            inscriptions_creees += 1
                    except Exception as e:
                        messages.warning(request, f'Erreur pour l\'employé {employee_id}: {str(e)}')
                
                if inscriptions_creees > 0:
                    messages.success(request, f'{inscriptions_creees} inscription(s) ajoutée(s) avec succès!')
                else:
                    messages.info(request, 'Aucune nouvelle inscription ajoutée.')
                return redirect('cours_programmes_home')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'inscription: {str(e)}')
                return redirect('cours_programmes_home')
    
    # GET request - gestion des vues et exports
    try:
        view_type = request.GET.get('view', 'list')
        query = request.GET.get('q', '').strip()
        statut_filter = request.GET.get('statut', '')
        date_filter = request.GET.get('date', '')
        
        # Filtrage des sessions
        sessions = Session.objects.select_related('formation', 'formateur').annotate(
            inscriptions_count=Count('inscription', filter=Q(inscription__statut__in=['inscrit', 'present']))
        ).all()
        
        if query:
            sessions = sessions.filter(
                Q(formation__titre__icontains=query) |
                Q(formation__code__icontains=query) |
                Q(formateur__nom__icontains=query) |
                Q(formateur__prenom__icontains=query)
            )
        
        if statut_filter:
            sessions = sessions.filter(statut=statut_filter)
        
        if date_filter:
            try:
                date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
                sessions = sessions.filter(date_debut__date=date_obj)
            except ValueError:
                pass
        
        sessions = sessions.order_by('date_debut')
        
        # Export PDF
        if request.GET.get('export') == 'pdf':
            return generate_sessions_pdf(sessions, query, statut_filter, date_filter)
        
        # Vue calendrier AJAX
        if view_type == 'calendar' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
            print("--- CALENDAR VIEW REQUEST RECEIVED ---")
            try:
                calendar_events = []
                print(f"Found {sessions.count()} sessions for the calendar.")

                for session in sessions:
                    calendar_events.append({
                        'id': session.id,
                        'title': f"{session.formation.code} - {session.formation.titre}",
                        'start': session.date_debut.isoformat(),
                        'end': session.date_fin.isoformat(),
                        'backgroundColor': get_status_color(session.statut),
                        'borderColor': get_status_color(session.statut),
                        'extendedProps': {
                            'formateur': f"{session.formateur.prenom} {session.formateur.nom}",
                            'lieu': session.lieu or 'Non défini',
                            'places': f"{getattr(session, 'inscriptions_count', 0)}/{session.places_totales}",
                            'statut': session.get_statut_display()
                        }
                    })
                
                print(f"--- PREPARING JSON RESPONSE WITH {len(calendar_events)} EVENTS ---")
                return JsonResponse(calendar_events, safe=False)
            except Exception as e:
                print(f"--- ERROR IN CALENDAR VIEW: {e} ---")
                return JsonResponse({'error': str(e)}, status=500)
        
        # Données pour les formulaires - CORRECTION: récupérer les employés avec les bons champs
        formations = Formation.objects.all().order_by('titre')
        formateurs = Formateur.objects.all().order_by('nom', 'prenom')
        # CORRECTION: utiliser les vrais champs de Employee
        employees = Employee.objects.filter(status='A').order_by('full_name')  # Seulement les actifs
        
        context = {
            'sessions': sessions,
            'formations': formations,
            'formateurs': formateurs,
            'employees': employees,
            'query': query,
            'statut_filter': statut_filter,
            'date_filter': date_filter,
            'view_type': view_type,
            'session_statuts': Session.STATUT_CHOICES,
            'today': timezone.now().date(),
        }
        
        # Gestion AJAX pour recherche
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and view_type == 'list':
            html_content = render_to_string('formation/cours_programmes.html', context)
            import re
            table_match = re.search(r'<tbody id="sessions-table">(.*?)</tbody>', html_content, re.DOTALL)
            if table_match:
                return HttpResponse(table_match.group(1))
            else:
                return HttpResponse('<tr><td colspan="7" class="text-center text-danger">Erreur: Impossible de trouver le tableau</td></tr>')
        
        return render(request, 'formation/cours_programmes.html', context)
        
    except Exception as e:
        print(f"Erreur dans la vue: {str(e)}")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=500)
        raise


def generate_sessions_pdf(sessions, query='', statut_filter='', date_filter=''):
    """Génère un PDF des sessions"""
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.units import inch
    from io import BytesIO
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Contenu du PDF
    story = []
    
    # Titre
    title_style = styles['Title']
    title = Paragraph("Programme des Sessions de Formation", title_style)
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Filtres appliqués
    if query or statut_filter or date_filter:
        filters = []
        if query:
            filters.append(f"Recherche: {query}")
        if statut_filter:
            filters.append(f"Statut: {statut_filter}")
        if date_filter:
            filters.append(f"Date: {date_filter}")
        
        filter_text = Paragraph(f"Filtres appliqués: {', '.join(filters)}", styles['Normal'])
        story.append(filter_text)
        story.append(Spacer(1, 12))
    
    # Tableau des sessions
    data = [['Code', 'Formation', 'Formateur', 'Début', 'Fin', 'Lieu', 'Places', 'Statut']]
    
    for session in sessions:
        data.append([
            session.formation.code,
            session.formation.titre[:30] + ('...' if len(session.formation.titre) > 30 else ''),
            f"{session.formateur.prenom} {session.formateur.nom}",
            session.date_debut.strftime('%d/%m/%Y %H:%M'),
            session.date_fin.strftime('%d/%m/%Y %H:%M'),
            session.lieu[:20] if session.lieu else '-',
            f"{getattr(session, 'inscriptions_count', 0)}/{session.places_totales}",
            session.get_statut_display()
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    
    # Génération du PDF
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="programme_sessions.pdf"'
    response.write(pdf)
    
    return response


###############

def formation_dashboard(request):
    """
    Vue pour le dashboard du module formation avec statistiques dynamiques
    """
    # Statistiques principales
    stats = {
        'total_formations': Formation.objects.count(),
        'sessions_actives': Session.objects.filter(
            statut__in=['planifiée', 'en_cours']
        ).count(),
        'total_participants': Inscription.objects.filter(
            statut__in=['inscrit', 'present']
        ).count(),
        'total_formateurs': Formateur.objects.count(),
    }
    
    # CORRECTION: Statistiques dynamiques par type de formation
    formation_instance = Formation()
    type_choices = dict(formation_instance.TYPE_CHOICES)
    
    # Générer les statistiques pour tous les types de formation disponibles
    formations_by_type = Formation.objects.values('type').annotate(
        count=Count('code')
    )
    
    # Initialiser toutes les statistiques de types à 0
    for type_value, type_label in formation_instance.TYPE_CHOICES:
        stats[f'formations_{type_value}'] = 0
    
    # Remplir avec les vraies valeurs
    for type_stat in formations_by_type:
        type_key = type_stat['type']
        if type_key:  # Vérifier que le type n'est pas None
            stats[f'formations_{type_key}'] = type_stat['count']
    
    # Créer une liste des types avec leurs statistiques pour l'affichage
    types_with_stats = []
    for type_value, type_label in formation_instance.TYPE_CHOICES:
        types_with_stats.append({
            'value': type_value,
            'label': type_label,
            'count': stats.get(f'formations_{type_value}', 0)
        })
    
    # Taux de présence moyen
    total_inscriptions = Inscription.objects.count()
    presents = Inscription.objects.filter(statut='present').count()
    stats['taux_presence'] = round((presents / total_inscriptions * 100) if total_inscriptions > 0 else 0, 1)
    
    # Score moyen des évaluations
    score_moyen = Evaluation.objects.aggregate(
        moyenne=Avg('score')
    )['moyenne']
    stats['score_moyen'] = round(score_moyen) if score_moyen else 0
    
    # Sessions récentes (5 dernières)
    recent_sessions = Session.objects.select_related(
        'formation', 'formateur'
    ).annotate(
        participants_count=Count('inscription')
    ).order_by('-date_debut')[:5]
    
    # Formations par domaine avec pourcentages
    formations_par_domaine = Formation.objects.values(
        'domaine'
    ).annotate(
        count=Count('code')
    ).order_by('-count')
    
    # Calculer les pourcentages pour les domaines
    total_formations = Formation.objects.count()
    domaine_choices = dict(formation_instance.DOMAINE_CHOICES)
    
    for domaine in formations_par_domaine:
        domaine['percentage'] = round(
            (domaine['count'] / total_formations * 100) if total_formations > 0 else 0, 1
        )
        # Ajouter le display name pour le domaine
        domaine['domaine__display'] = domaine_choices.get(domaine['domaine'], domaine['domaine'])
    
    # NOUVEAU: Formations par type avec pourcentages pour le graphique
    formations_par_type = []
    for type_stat in types_with_stats:
        if type_stat['count'] > 0:  # Ne montrer que les types avec des formations
            percentage = round((type_stat['count'] / total_formations * 100) if total_formations > 0 else 0, 1)
            formations_par_type.append({
                'type': type_stat['value'],
                'type_display': type_stat['label'],
                'count': type_stat['count'],
                'percentage': percentage
            })
    
    # Top formateurs (par nombre de sessions)
    top_formateurs = Formateur.objects.annotate(
        sessions_count=Count('session')
    ).filter(
        sessions_count__gt=0
    ).order_by('-sessions_count')[:5]
    
    # Alertes et notifications
    # 1. Sessions à venir cette semaine
    today = timezone.now()
    week_end = today + timedelta(days=7)
    upcoming_sessions = Session.objects.filter(
        date_debut__gte=today,
        date_debut__lte=week_end,
        statut__in=['planifiée', 'en_cours']
    )
    
    # 2. Sessions avec places limitées (moins de 3 places disponibles)
    sessions_places_limitees = []
    for session in Session.objects.filter(statut__in=['planifiée', 'en_cours']):
        participants_count = Inscription.objects.filter(
            session=session,
            statut__in=['inscrit', 'present']
        ).count()
        places_disponibles = session.places_totales - participants_count
        if places_disponibles <= 3 and places_disponibles >= 0:
            sessions_places_limitees.append(session)
    
    # Listes pour les modals d'actions rapides
    formations_list = Formation.objects.all().order_by('titre')
    formateurs_list = Formateur.objects.all().order_by('nom', 'prenom')
    suppliers_list = Supplier.objects.all().order_by('name')

    # Créer des listes avec les choix de domaines dynamiques
    domaines_choices = []
    for value, label in formation_instance.DOMAINE_CHOICES:
        domaines_choices.append({
            'value': value,
            'label': label
        })
    
    context = {
        'stats': stats,
        'types_with_stats': types_with_stats,  # NOUVEAU
        'formations_par_type': formations_par_type,  # NOUVEAU
        'recent_sessions': recent_sessions,
        'formations_par_domaine': formations_par_domaine,
        'top_formateurs': top_formateurs,
        'upcoming_sessions': upcoming_sessions,
        'sessions_places_limitees': sessions_places_limitees,
        'formations_list': formations_list,
        'formateurs_list': formateurs_list,
        'suppliers_list': suppliers_list,  # AJOUTÉ: Fournisseurs pour le modal
        'domaines_choices': domaines_choices,
        
    }
    
    return render(request, 'formation/dashboard_index.html', context)

###########

def get_config_file_path():
    """Retourne le chemin du fichier de configuration"""
    return os.path.join(settings.BASE_DIR, 'formation_config.json')

def load_config():
    """Charge la configuration depuis le fichier JSON"""
    config_file = get_config_file_path()
    default_config = {
        'formation_types': [
            {'value': 'interne', 'label': 'Interne'},
            {'value': 'externe', 'label': 'Externe'},
            {'value': 'e_learning', 'label': 'E-learning'},
        ],
        'formation_domaines': [
            {'value': 'IT', 'label': 'Informatique'},
            {'value': 'HR', 'label': 'Ressources Humaines'},
            {'value': 'Finance', 'label': 'Finance'},
            {'value': 'life', 'label': 'Life'},
            {'value': 'economie', 'label': 'Économie'},
            {'value': 'medecine', 'label': 'Médecine'},
            {'value': 'management', 'label': 'Management'},
            {'value': 'qualite', 'label': 'Qualité'},
            {'value': 'securite', 'label': 'Sécurité'},
            {'value': 'marketing', 'label': 'Marketing'},
        ]
    }
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Créer le fichier avec la configuration par défaut
            save_config(default_config)
            return default_config
    except Exception as e:
        print(f"Erreur lors du chargement de la configuration: {e}")
        return default_config

def save_config(config):
    """Sauvegarde la configuration dans le fichier JSON"""
    config_file = get_config_file_path()
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la configuration: {e}")
        return False

def configuration_home(request):
    """
    Vue principale pour la gestion des configurations de formation
    Gère l'affichage, l'ajout, la modification et la suppression des types et domaines
    """
    
    if request.method == 'POST':
        action = request.POST.get('action')
        category = request.POST.get('category')  # 'types' ou 'domaines'
        
        if action == 'add':
            try:
                value = request.POST.get('value', '').strip()
                label = request.POST.get('label', '').strip()
                
                if not value or not label:
                    messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
                    return redirect('configuration_home')
                
                # Charger la configuration actuelle
                config = load_config()
                
                # Déterminer la liste à modifier
                if category == 'types':
                    target_list = config['formation_types']
                    success_msg = f'Type de formation "{label}" ajouté avec succès!'
                elif category == 'domaines':
                    target_list = config['formation_domaines']
                    success_msg = f'Domaine de formation "{label}" ajouté avec succès!'
                else:
                    messages.error(request, 'Catégorie invalide.')
                    return redirect('configuration_home')
                
                # Vérifier que la valeur n'existe pas déjà
                if any(item['value'] == value for item in target_list):
                    messages.error(request, 'Cette valeur existe déjà.')
                    return redirect('configuration_home')
                
                # Ajouter le nouvel élément
                target_list.append({'value': value, 'label': label})
                
                # Sauvegarder
                if save_config(config):
                    messages.success(request, success_msg)
                else:
                    messages.error(request, 'Erreur lors de la sauvegarde.')
                
                return redirect('configuration_home')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'ajout: {str(e)}')
                return redirect('configuration_home')
        
        elif action == 'edit':
            try:
                old_value = request.POST.get('old_value')
                new_value = request.POST.get('value', '').strip()
                new_label = request.POST.get('label', '').strip()
                
                if not old_value or not new_value or not new_label:
                    messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
                    return redirect('configuration_home')
                
                # Charger la configuration actuelle
                config = load_config()
                
                # Déterminer la liste à modifier
                if category == 'types':
                    target_list = config['formation_types']
                    success_msg = f'Type de formation "{new_label}" modifié avec succès!'
                elif category == 'domaines':
                    target_list = config['formation_domaines']
                    success_msg = f'Domaine de formation "{new_label}" modifié avec succès!'
                else:
                    messages.error(request, 'Catégorie invalide.')
                    return redirect('configuration_home')
                
                # Trouver et modifier l'élément
                item_found = False
                for item in target_list:
                    if item['value'] == old_value:
                        # Vérifier que la nouvelle valeur n'existe pas déjà (sauf si c'est la même)
                        if new_value != old_value and any(i['value'] == new_value for i in target_list):
                            messages.error(request, 'Cette nouvelle valeur existe déjà.')
                            return redirect('configuration_home')
                        
                        item['value'] = new_value
                        item['label'] = new_label
                        item_found = True
                        break
                
                if not item_found:
                    messages.error(request, 'Élément introuvable.')
                    return redirect('configuration_home')
                
                # Sauvegarder
                if save_config(config):
                    messages.success(request, success_msg)
                else:
                    messages.error(request, 'Erreur lors de la sauvegarde.')
                
                return redirect('configuration_home')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification: {str(e)}')
                return redirect('configuration_home')
        
        elif action == 'delete':
            try:
                value = request.POST.get('value')
                
                if not value:
                    messages.error(request, 'Valeur manquante.')
                    return redirect('configuration_home')
                
                # Charger la configuration actuelle
                config = load_config()
                
                # Déterminer la liste à modifier
                if category == 'types':
                    target_list = config['formation_types']
                    success_msg = 'Type de formation supprimé avec succès!'
                elif category == 'domaines':
                    target_list = config['formation_domaines']
                    success_msg = 'Domaine de formation supprimé avec succès!'
                else:
                    messages.error(request, 'Catégorie invalide.')
                    return redirect('configuration_home')
                
                # Trouver et supprimer l'élément
                original_length = len(target_list)
                config[f'formation_{category}'] = [item for item in target_list if item['value'] != value]
                
                if len(config[f'formation_{category}']) == original_length:
                    messages.error(request, 'Élément introuvable.')
                    return redirect('configuration_home')
                
                # Sauvegarder
                if save_config(config):
                    messages.success(request, success_msg)
                else:
                    messages.error(request, 'Erreur lors de la sauvegarde.')
                
                return redirect('configuration_home')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la suppression: {str(e)}')
                return redirect('configuration_home')
    
    # GET request - affichage de la configuration
    try:
        query = request.GET.get('q', '').strip()
        category_filter = request.GET.get('category', 'all')
        
        config = load_config()
        
        # Filtrer selon la recherche et la catégorie
        types_list = config['formation_types']
        domaines_list = config['formation_domaines']
        
        if query:
            types_list = [item for item in types_list if query.lower() in item['label'].lower() or query.lower() in item['value'].lower()]
            domaines_list = [item for item in domaines_list if query.lower() in item['label'].lower() or query.lower() in item['value'].lower()]
        
        # CORRECTION PRINCIPALE : Utiliser les listes filtrées dans le contexte
        context = {
            'formation_types': types_list,  # Utiliser la liste filtrée
            'formation_domaines': domaines_list,  # Utiliser la liste filtrée
            'query': query,
            'category_filter': category_filter,
        }
        
        # Gestion des requêtes AJAX pour la recherche
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html_content = render_to_string('formation/configuration_index.html', context)
            # Extraire seulement la partie des tableaux
            import re
            content_match = re.search(r'<div class="content">(.*?)</div>(?=\s*<script)', html_content, re.DOTALL)
            if content_match:
                return HttpResponse(content_match.group(1))
            else:
                return HttpResponse('<div class="text-center text-danger">Erreur: Impossible de charger le contenu</div>')
        
        return render(request, 'formation/configuration_index.html', context)
        
    except Exception as e:
        print(f"Erreur dans la vue configuration: {str(e)}")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'error': str(e)}, status=500)
        messages.error(request, f'Erreur lors du chargement de la configuration: {str(e)}')
        return redirect('formation_home')