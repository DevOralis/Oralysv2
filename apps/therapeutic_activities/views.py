from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.views.decorators.http import require_GET, require_POST
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
import json
import logging
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from apps.hr.models.employee import Employee
from apps.patient.models import Patient

from .models import (
    ActivityType, ActivityLocation, Activity, Session, 
    Participation, ErgotherapyEvaluation, CoachingSession, SocialReport
)
from .forms import (
    ActivityTypeForm, ActivityLocationForm, ActivityForm, SessionForm,
    ParticipationForm, ErgotherapyEvaluationForm, CoachingSessionForm, SocialReportForm,
    SessionSearchForm, ParticipationSearchForm, BulkParticipationForm
)

logger = logging.getLogger(__name__)

# ========================================
# VUES D'ACCUEIL ET MENU
# ========================================

def activities_home(request):
    try:
        # Statistiques générales
        total_activities = Activity.objects.filter(is_active=True).count()
        total_sessions = Session.objects.count()
        total_participations = Participation.objects.count()
        
        # Sessions à venir
        upcoming_sessions = Session.objects.filter(
            status='planned',
            date__gte=timezone.now().date()
        ).order_by('date', 'start_time')[:5]
        
        # Sessions d'aujourd'hui
        today_sessions = Session.objects.filter(
            date=timezone.now().date(),
            status='planned'
        ).order_by('start_time')
        
        # Statistiques par type d'activité
        activity_types_stats = ActivityType.objects.annotate(
            activities_count=Count('activity'),
            sessions_count=Count('activity__sessions')
        ).order_by('-sessions_count')[:5]
        
        # Top coaches
        top_coaches = Activity.objects.values('coach__full_name').annotate(
            sessions_count=Count('sessions')
        ).filter(coach__isnull=False).order_by('-sessions_count')[:5]
        
        context = {
            'page_title': 'Activités & Thérapies Paramédicales',
                'total_activities': total_activities,
                'total_sessions': total_sessions,
                'total_participations': total_participations,
                'upcoming_sessions': upcoming_sessions,
                'today_sessions': today_sessions,
                'activity_types_stats': activity_types_stats,
                'top_coaches': top_coaches,
        }
        return render(request, 'activities_home.html', context)
    except Exception as e:
        logger.error(f"Erreur dans activities_home: {e}")
        messages.error(request, "Une erreur est survenue lors du chargement de la page d'accueil.")
        return render(request, 'activities_home.html', {})

# ========================================
# VUES DE CONFIGURATION
# ========================================

def configuration(request):
    try:
        tab = request.GET.get('tab', 'activity_types')
        
        # Données pour chaque onglet (sans pagination côté serveur)
        activity_types = ActivityType.objects.all().order_by('name')
        activity_locations = ActivityLocation.objects.all().order_by('name')
        
        context = {
            'page_title': 'Configuration - Activités Thérapeutiques',
            'tab': tab,
            'activity_types': activity_types,
            'activity_locations': activity_locations,
            'activity_type_form': ActivityTypeForm(),
            'activity_location_form': ActivityLocationForm(),
        }
        return render(request, 'therapeutic_activities_configuration.html', context)
    except Exception as e:
        logger.error(f"Erreur dans configuration: {e}")
        messages.error(request, "Une erreur est survenue lors du chargement de la configuration.")
        return redirect('therapeutic_activities:activities_home')

# ========================================
# VUES D'ACTIVITÉS
# ========================================
def activity_list(request):
    # Gestion affichage formulaire (inline comme dans inventory)
    action_form = request.GET.get('form', '')
    show_form = False
    activity_obj = None
    form_instance = None
    if action_form == 'create':
        show_form = True
        form_instance = ActivityForm()
    elif action_form == 'edit':
        pk_edit = request.GET.get('id')
        if pk_edit:
            activity_obj = get_object_or_404(Activity, pk=pk_edit)
            form_instance = ActivityForm(instance=activity_obj)
            show_form = True

    # Données sans pagination côté serveur (pagination JavaScript)
    activities = Activity.objects.select_related('type', 'coach').annotate(
        total_sessions=Count('sessions')
    ).order_by('title')

    # Filtres dropdown pour les formulaires (pas de filtrage côté serveur)
    activity_types = ActivityType.objects.filter(is_active=True).order_by('name')
    coaches = Employee.objects.filter(
                status='A',
                position__name__iexact='coach'
            ).order_by('full_name')

    context = {
        'page_title': 'Liste des Activités',
        'activities': activities,
        'activity_types': activity_types,
        'coaches': coaches,
        'show_form': show_form,
        'form': form_instance,
        'activity': activity_obj,
    }
    return render(request, 'activity_list.html', context)

def activity_create(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Activité créée avec succès.")
            return redirect("therapeutic_activities:activity_list")
    else:
        form = ActivityForm()

    return render(request, 'activity_form.html', {
        'page_title': "Créer une activité",
        'form': form,
    })

# ----------------------------
def activity_edit(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    if request.method == "POST":
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            return redirect("therapeutic_activities:activity_list")
    else:
        form = ActivityForm(instance=activity)

    return render(request, "activity_form.html", {"form": form, "activity": activity})

# ----------------------------
@csrf_exempt
def activity_delete(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    if request.method == "POST":
        activity.delete()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True})
        return HttpResponseRedirect(reverse("therapeutic_activities:activity_list"))
    return JsonResponse({"success": False, "error": "Méthode invalide"}, status=400)

def activity_preview(request, pk):
    """Return JSON with rendered HTML preview card for an activity."""
    try:
        activity = get_object_or_404(Activity.objects.select_related('type', 'coach'), pk=pk)
        html = render_to_string('activity_preview_card.html', {'activity': activity})
        return JsonResponse({'success': True, 'html': html, 'title': activity.title})
    except Exception as e:
        logger.error(f"Erreur dans activity_preview: {e}")
        return JsonResponse({'success': False, 'message': "Erreur lors du chargement de l'aperçu."}, status=500)
# ========================================
# VUES DE SESSIONS
# ========================================

def session_list(request):
    try:
        # Gestion des requêtes POST (ajout et modification)
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'add':
                form = SessionForm(request.POST)
                if form.is_valid():
                    session = form.save()
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True,
                            'message': 'Session ajoutée avec succès.'
                        })
                    messages.success(request, 'Session ajoutée avec succès.')
                    return redirect('therapeutic_activities:session_list')
                else:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'message': 'Erreur dans le formulaire. Veuillez vérifier les champs.',
                            'errors': form.errors
                        })
                    messages.error(request, 'Erreur dans le formulaire.')
            
            elif action == 'edit':
                session_id = request.POST.get('session_id')
                if session_id:
                    session = get_object_or_404(Session, pk=session_id)
                    form = SessionForm(request.POST, instance=session)
                    if form.is_valid():
                        session = form.save()
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': True,
                                'message': 'Session modifiée avec succès.'
                            })
                        messages.success(request, 'Session modifiée avec succès.')
                        return redirect('therapeutic_activities:session_list')
                    else:
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': False,
                                'message': 'Erreur dans le formulaire. Veuillez vérifier les champs.',
                                'errors': form.errors
                            })
                        messages.error(request, 'Erreur dans le formulaire.')
        
        # Données sans pagination côté serveur (pagination JavaScript)
        sessions = Session.objects.select_related('activity', 'location', 'activity__coach').order_by('date', 'start_time')
        
        context = {
            'page_title': 'Liste des Sessions',
            'sessions': sessions,
            'activities': Activity.objects.filter(is_active=True).order_by('title'),
            'locations': ActivityLocation.objects.filter(is_active=True).order_by('name'),
            'session_form': SessionForm(),
        }
        return render(request, 'session_list.html', context)
    except Exception as e:
        logger.error(f"Erreur dans session_list: {e}")
        messages.error(request, "Une erreur est survenue lors du chargement de la liste des sessions.")
        return render(request, 'session_list.html', {})

def session_create(request):
    try:
        if request.method == 'POST':
            form = SessionForm(request.POST)
            if form.is_valid():
                session = form.save()
                messages.success(request, 'Session créée avec succès. Vous pouvez maintenant ajouter des participants.')
                return redirect('therapeutic_activities:participation_list')
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Erreur lors de la création de la session. Veuillez vérifier les champs.'
                    })
        else:
            form = SessionForm()
        
        context = {
            'page_title': 'Créer une Session',
            'form': form,
        }
        return render(request, 'session_form.html', context)
    except Exception as e:
        logger.error(f"Erreur dans session_create: {e}")
        return redirect(f"{reverse('therapeutic_activities:session_list')}?message=Erreur%20lors%20de%20la%20création&type=error")

def session_edit(request, pk):
    try:
        session = get_object_or_404(Session, pk=pk)
        
        if request.method == 'POST':
            form = SessionForm(request.POST, instance=session)
            if form.is_valid():
                session = form.save()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                    return JsonResponse({
                        'success': True,
                        'message': 'Session modifiée avec succès.'
                    })
                return redirect(f"{reverse('therapeutic_activities:session_list')}?message=Session%20modifiée%20avec%20succès&type=success")
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Erreur lors de la modification de la session. Veuillez vérifier les champs.'
                    })
        else:
            form = SessionForm(instance=session)
        
        context = {
            'page_title': 'Modifier la session',
            'form': form,
            'session': session,
        }
        return render(request, 'session_form.html', context)
    except Exception as e:
        logger.error(f"Erreur dans session_edit: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({
                'success': False,
                'message': 'Une erreur est survenue lors de la modification.'
            })
        return redirect(f"{reverse('therapeutic_activities:session_list')}?message=Erreur%20lors%20de%20la%20modification&type=error")

def session_delete(request, pk):
    try:
        session = get_object_or_404(Session, pk=pk)
        
        if request.method == 'POST':
            # Vérifier s'il y a des participations
            if session.participants.exists():
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                    return JsonResponse({
                        'success': False,
                        'message': 'Impossible de supprimer la session car elle a des participants inscrits.'
                    })
                messages.error(request, 'Impossible de supprimer la session car elle a des participants inscrits.')
                return redirect('therapeutic_activities:session_list')
                
            session.delete()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': 'Session supprimée avec succès.'
                })
            
            messages.success(request, 'Session supprimée avec succès.')
            return redirect('therapeutic_activities:session_list')
        
        context = {
            'page_title': 'Supprimer la session',
            'session': session,
        }
        return render(request, 'session_confirm_delete.html', context)
    except Exception as e:
        logger.error(f"Erreur dans session_delete: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({
                'success': False,
                'message': 'Une erreur est survenue lors de la suppression.'
            })
        messages.error(request, "Une erreur est survenue lors de la suppression de la session.")
        return redirect('therapeutic_activities:session_list')

# ========================================
# VUES DE PARTICIPATION
# ========================================

def participation_list(request):
    try:
        # Récupérer toutes les participations pour le filtrage côté client
        participations = Participation.objects.select_related('patient', 'session', 'session__activity', 'session__location').order_by('session__date', 'session__start_time')
        
        context = {
            'page_title': 'Liste des Participations',
            'participations': participations,
            'sessions': Session.objects.all().order_by('date', 'start_time'),
            'patients': Patient.objects.all().order_by('last_name', 'first_name'),
            'participation_form': ParticipationForm(),
            'bulk_form': BulkParticipationForm(),
        }
        return render(request, 'participation_list.html', context)
    except Exception as e:
        logger.error(f"Erreur dans participation_list: {e}")
        messages.error(request, "Une erreur est survenue lors du chargement de la liste des participations.")
        return render(request, 'participation_list.html', {})

def participation_create(request):
    try:
        if request.method == 'POST':
            form = ParticipationForm(request.POST)
            logger.info(f"POST data: {request.POST}")
            if form.is_valid():
                participation = form.save()
                
                # Retour AJAX avec succès
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'Participation créée avec succès.',
                        'redirect_url': reverse('therapeutic_activities:participation_list')
                    })
                
                messages.success(request, f'Participation créée avec succès.')
                return redirect('therapeutic_activities:participation_list')
            else:
                logger.error(f"Erreurs du formulaire: {form.errors}")
                
                # Retour AJAX avec erreur
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    error_message = "Erreur lors de la création de la participation :\n"
                    
                    # Traiter les erreurs de champs spécifiques
                    for field, errors in form.errors.items():
                        if field == '__all__':
                            # Erreurs globales (comme le doublon)
                            for error in errors:
                                error_message += f"• {error}\n"
                        else:
                            # Erreurs de champs spécifiques
                            field_name = form.fields[field].label or field
                            for error in errors:
                                error_message += f"• {field_name}: {error}\n"
                    
                    return JsonResponse({
                        'success': False,
                        'message': error_message.strip(),
                        'errors': form.errors
                    })
                
                messages.error(request, f'Erreur lors de la création: {form.errors}')
        else:
            form = ParticipationForm()
        
        context = {
            'page_title': 'Créer une Participation',
            'form': form,
        }
        return render(request, 'participation_form.html', context)
    except Exception as e:
        logger.error(f"Erreur dans participation_create: {e}")
        messages.error(request, "Une erreur est survenue lors de la création de la participation.")
        return redirect('therapeutic_activities:participation_list')

def participation_edit(request, pk):
    try:
        participation = get_object_or_404(Participation, pk=pk)
        
        if request.method == 'POST':
            form = ParticipationForm(request.POST, instance=participation)
            if form.is_valid():
                participation = form.save()
                messages.success(request, f'Participation modifiée avec succès.')
                return redirect('therapeutic_activities:participation_list')
            else:
                messages.error(request, 'Erreur lors de la modification de la participation.')
        else:
            form = ParticipationForm(instance=participation)
        
        context = {
            'page_title': f'Modifier la participation',
            'form': form,
            'participation': participation,
        }
        return render(request, 'participation_form.html', context)
    except Exception as e:
        logger.error(f"Erreur dans participation_edit: {e}")
        messages.error(request, "Une erreur est survenue lors de la modification de la participation.")
        return redirect('therapeutic_activities:participation_list')

def participation_delete(request, pk):
    try:
        participation = get_object_or_404(Participation, pk=pk)
        
        if request.method == 'POST':
            participation.delete()
            messages.success(request, 'Participation supprimée avec succès.')
            return redirect('therapeutic_activities:participation_list')
        
        context = {
            'page_title': 'Supprimer la participation',
            'participation': participation,
        }
        return render(request, 'participation_confirm_delete.html', context)
    except Exception as e:
        logger.error(f"Erreur dans participation_delete: {e}")
        messages.error(request, "Une erreur est survenue lors de la suppression de la participation.")
        return redirect('therapeutic_activities:participation_list')

# ========================================
# VUES AJAX POUR CONFIGURATION
# ========================================

@require_GET
def search_activity_types(request):
    try:
        query = request.GET.get('q', '')
        activity_types = ActivityType.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).order_by('name')
        
        html = render_to_string('activity_type_table_body.html', {
            'activity_types': activity_types
        })
        return JsonResponse({'html': html})
    except Exception as e:
        logger.error(f"Erreur dans search_activity_types: {e}")
        return JsonResponse({'error': 'Erreur lors de la recherche'}, status=500)

@require_GET
def search_activity_locations(request):
    try:
        query = request.GET.get('q', '')
        locations = ActivityLocation.objects.filter(
            Q(name__icontains=query) | Q(address__icontains=query)
        ).order_by('name')
        
        html = render_to_string('activity_location_table_body.html', {
            'activity_locations': locations
        })
        return JsonResponse({'html': html})
    except Exception as e:
        logger.error(f"Erreur dans search_activity_locations: {e}")
        return JsonResponse({'error': 'Erreur lors de la recherche'}, status=500)

# ========================================
# VUES AJAX POUR CRUD
# ========================================

@require_POST
@csrf_exempt
def create_activity_type(request):
    try:
        # Log pour identifier quelle vue est appelée
        logger.info("=== VUE CREATE_ACTIVITY_TYPE APPELÉE ===")
        
        data = json.loads(request.body)
        logger.info(f"Données reçues pour création ActivityType: {data}")
        
        form = ActivityTypeForm(data)
        if form.is_valid():
            activity_type = form.save()
            logger.info(f"ActivityType créé avec succès: {activity_type.name}")
            return JsonResponse({
                'success': True,
                'message': f'Type d\'activité "{activity_type.name}" créé avec succès.',
                'id': activity_type.id,
                'name': activity_type.name
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    except Exception as e:
        logger.error(f"Erreur dans create_activity_type: {e}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@require_POST
@csrf_exempt
def create_activity_location(request):
    try:
        data = json.loads(request.body)
        form = ActivityLocationForm(data)
        if form.is_valid():
            location = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Salle "{location.name}" créée avec succès.',
                'id': location.id,
                'name': location.name
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    except Exception as e:
        logger.error(f"Erreur dans create_activity_location: {e}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@require_POST
@csrf_exempt
def delete_activity_type(request, pk=None):
    try:
        # Essayer d'abord de récupérer l'ID depuis l'URL
        if pk:
            activity_type_id = pk
        else:
            # Sinon, essayer depuis le corps de la requête (pour compatibilité)
            data = json.loads(request.body)
            activity_type_id = data.get('id')
        
        activity_type = get_object_or_404(ActivityType, id=activity_type_id)
        
        # Vérifier s'il y a des activités liées
        if activity_type.activity_set.exists():
            return JsonResponse({
                'success': False,
                'message': 'Impossible de supprimer ce type car il a des activités associées.'
            })
        
        name = activity_type.name
        activity_type.delete()
        return JsonResponse({
            'success': True,
            'message': f'Type d\'activité "{name}" supprimé avec succès.'
        })
    except Exception as e:
        logger.error(f"Erreur dans delete_activity_type: {e}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@require_POST
@csrf_exempt
def delete_activity_location(request, pk=None):
    try:
        # Essayer d'abord de récupérer l'ID depuis l'URL
        if pk:
            location_id = pk
        else:
            # Sinon, essayer depuis le corps de la requête (pour compatibilité)
            data = json.loads(request.body)
            location_id = data.get('id')
        
        location = get_object_or_404(ActivityLocation, id=location_id)
        
        # Vérifier s'il y a des sessions liées
        if location.session_set.exists():
            return JsonResponse({
                'success': False,
                'message': 'Impossible de supprimer cette salle car elle a des sessions associées.'
            })
        
        name = location.name
        location.delete()
        return JsonResponse({
            'success': True,
            'message': f'Salle "{name}" supprimée avec succès.'
        })
    except Exception as e:
        logger.error(f"Erreur dans delete_activity_location: {e}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@require_POST
@csrf_exempt
def update_activity_type(request, pk):
    try:
        # Log pour identifier quelle vue est appelée
        logger.info(f"=== VUE UPDATE_ACTIVITY_TYPE APPELÉE AVEC PK={pk} ===")
        
        activity_type = get_object_or_404(ActivityType, pk=pk)
        data = json.loads(request.body)
        
        # Debug: log des données reçues
        logger.info(f"Données reçues pour modification ActivityType {pk}: {data}")
        
        # Créer le formulaire avec l'instance existante
        form = ActivityTypeForm(data, instance=activity_type)
        if form.is_valid():
            # Sauvegarder les modifications sur l'instance existante
            updated_activity_type = form.save()
            logger.info(f"ActivityType {pk} modifié avec succès: {updated_activity_type.name}")
            return JsonResponse({
                'success': True,
                'message': f'Type d\'activité "{updated_activity_type.name}" modifié avec succès.',
                'id': updated_activity_type.id,
                'name': updated_activity_type.name
            })
        else:
            logger.error(f"Erreurs de validation pour ActivityType {pk}: {form.errors}")
            return JsonResponse({
                'success': False,
                'message': 'Erreur de validation du formulaire.',
                'errors': form.errors
            })
    except Exception as e:
        logger.error(f"Erreur dans update_activity_type: {e}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@require_POST
@csrf_exempt
def update_activity_location(request, pk):
    try:
        location = get_object_or_404(ActivityLocation, pk=pk)
        data = json.loads(request.body)
        
        # Debug: log des données reçues
        logger.info(f"Données reçues pour modification ActivityLocation {pk}: {data}")
        
        # Créer le formulaire avec l'instance existante
        form = ActivityLocationForm(data, instance=location)
        if form.is_valid():
            # Sauvegarder les modifications sur l'instance existante
            updated_location = form.save()
            logger.info(f"ActivityLocation {pk} modifiée avec succès")
            return JsonResponse({
                'success': True,
                'message': f'Salle "{updated_location.name}" modifiée avec succès.',
                'id': updated_location.id,
                'name': updated_location.name
            })
        else:
            logger.error(f"Erreurs de validation pour ActivityLocation {pk}: {form.errors}")
            return JsonResponse({
                'success': False,
                'message': 'Erreur de validation du formulaire.',
                'errors': form.errors
            })
    except Exception as e:
        logger.error(f"Erreur dans update_activity_location: {e}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

# ========================================
# VUES D'ÉVALUATIONS SPÉCIALISÉES
# ========================================

def ergotherapy_evaluation_create(request, participation_pk):
    try:
        participation = get_object_or_404(Participation, pk=participation_pk)
        
        # Vérifier si une évaluation existe déjà
        if hasattr(participation, 'ergo_eval'):
                messages.warning(request, 'Une évaluation ergothérapique existe déjà pour cette participation.')
                return redirect('therapeutic_activities:participation_list')
            
        if request.method == 'POST':
            form = ErgotherapyEvaluationForm(request.POST)
            if form.is_valid():
                evaluation = form.save(commit=False)
                evaluation.participation = participation
                evaluation.save()
                messages.success(request, 'Évaluation ergothérapique créée avec succès.')
                return redirect('therapeutic_activities:participation_list')
            else:
                messages.error(request, 'Erreur lors de la création de l\'évaluation.')
        else:
            form = ErgotherapyEvaluationForm()
        
        context = {
            'page_title': f'Évaluation ergothérapique - {participation.patient}',
            'form': form,
            'participation': participation,
        }
        return render(request, 'ergotherapy_evaluation_form.html', context)
    except Exception as e:
        logger.error(f"Erreur dans ergotherapy_evaluation_create: {e}")
        messages.error(request, "Une erreur est survenue lors de la création de l'évaluation.")
        return redirect('therapeutic_activities:participation_list')

def coaching_session_create(request, participation_pk):
    try:
        participation = get_object_or_404(Participation, pk=participation_pk)
        
            # Vérifier si une session de coaching existe déjà
        if hasattr(participation, 'coaching'):
            messages.warning(request, 'Une session de coaching existe déjà pour cette participation.')
            return redirect('therapeutic_activities:participation_list')
            
        if request.method == 'POST':
            form = CoachingSessionForm(request.POST)
            if form.is_valid():
                coaching = form.save(commit=False)
                coaching.participation = participation
                coaching.save()
                messages.success(request, 'Session de coaching créée avec succès.')
                return redirect('therapeutic_activities:participation_list')
            else:
                messages.error(request, 'Erreur lors de la création de la session de coaching.')
        else:
            form = CoachingSessionForm()
        
        context = {
            'page_title': f'Session de coaching - {participation.patient}',
            'form': form,
            'participation': participation,
        }
        return render(request, 'coaching_session_form.html', context)
    except Exception as e:
        logger.error(f"Erreur dans coaching_session_create: {e}")
        messages.error(request, "Une erreur est survenue lors de la création de la session de coaching.")
        return redirect('therapeutic_activities:participation_list')

def social_report_create(request, participation_pk):
    try:
        participation = get_object_or_404(Participation, pk=participation_pk)
        
        # Vérifier si un rapport social existe déjà
        if hasattr(participation, 'social_report'):
            messages.warning(request, 'Un rapport social existe déjà pour cette participation.')
            return redirect('therapeutic_activities:participation_list')
            
        if request.method == 'POST':
            form = SocialReportForm(request.POST)
            if form.is_valid():
                report = form.save(commit=False)
                report.participation = participation
                report.save()
                messages.success(request, 'Rapport social créé avec succès.')
                return redirect('therapeutic_activities:participation_list')
            else:
                messages.error(request, 'Erreur lors de la création du rapport social.')
        else:
            form = SocialReportForm()
        
        context = {
            'page_title': f'Rapport social - {participation.patient}',
            'form': form,
            'participation': participation,
        }
        return render(request, 'social_report_form.html', context)
    except Exception as e:
        logger.error(f"Erreur dans social_report_create: {e}")
        messages.error(request, "Une erreur est survenue lors de la création du rapport social.")
        return redirect('therapeutic_activities:participation_list')

# ========================================
# NOUVELLES VUES POUR ÉVALUATIONS SPÉCIALISÉES
# ========================================

def ergotherapy_evaluation_detail(request, participation_pk):
    try:
        participation = get_object_or_404(Participation, pk=participation_pk)
        evaluation = get_object_or_404(ErgotherapyEvaluation, participation=participation)
        
        context = {
            'page_title': f'Évaluation ergothérapique - {participation.patient}',
            'evaluation': evaluation,
            'participation': participation,
        }
        return render(request, 'ergotherapy_evaluation_detail.html', context)
    except Exception as e:
        logger.error(f"Erreur dans ergotherapy_evaluation_detail: {e}")
        messages.error(request, "Une erreur est survenue lors du chargement de l'évaluation.")
        return redirect('therapeutic_activities:participation_list')

def ergotherapy_evaluation_edit(request, participation_pk):
    try:
        participation = get_object_or_404(Participation, pk=participation_pk)
        evaluation = get_object_or_404(ErgotherapyEvaluation, participation=participation)
        
        if request.method == 'POST':
            form = ErgotherapyEvaluationForm(request.POST, instance=evaluation)
            if form.is_valid():
                evaluation = form.save()
                messages.success(request, 'Évaluation ergothérapique modifiée avec succès.')
                return redirect('therapeutic_activities:participation_list')
            else:
                messages.error(request, 'Erreur lors de la modification de l\'évaluation.')
        else:
            form = ErgotherapyEvaluationForm(instance=evaluation)
        
        context = {
            'page_title': f'Modifier l\'évaluation ergothérapique - {participation.patient}',
            'form': form,
            'participation': participation,
            'evaluation': evaluation,
        }
        return render(request, 'ergotherapy_evaluation_form.html', context)
    except Exception as e:
        logger.error(f"Erreur dans ergotherapy_evaluation_edit: {e}")
        messages.error(request, "Une erreur est survenue lors de la modification de l'évaluation.")
        return redirect('therapeutic_activities:participation_list')

def coaching_session_detail(request, participation_pk):             
    try:
        participation = get_object_or_404(Participation, pk=participation_pk)
        coaching = get_object_or_404(CoachingSession, participation=participation)
        
        context = {
            'page_title': f'Session de coaching - {participation.patient}',
            'coaching': coaching,
            'participation': participation,
        }
        return render(request, 'coaching_session_detail.html', context)
    except Exception as e:
        logger.error(f"Erreur dans coaching_session_detail: {e}")
        messages.error(request, "Une erreur est survenue lors du chargement de la session de coaching.")
        return redirect('therapeutic_activities:coaching_session_list')

def coaching_session_edit(request, participation_pk):
    try:
        participation = get_object_or_404(Participation, pk=participation_pk)
        coaching = get_object_or_404(CoachingSession, participation=participation)
        
        if request.method == 'POST':
            form = CoachingSessionForm(request.POST, instance=coaching)
            if form.is_valid():
                coaching = form.save()
                messages.success(request, 'Session de coaching modifiée avec succès.')
                return redirect('therapeutic_activities:coaching_session_list')
            else:
                messages.error(request, 'Erreur lors de la modification de la session de coaching.')
        else:
            form = CoachingSessionForm(instance=coaching)
        
        context = {
            'page_title': f'Modifier la session de coaching - {participation.patient}',
            'form': form,
            'participation': participation,
            'coaching': coaching,
        }
        return render(request, 'coaching_session_form.html', context)
    except Exception as e:
        logger.error(f"Erreur dans coaching_session_edit: {e}")
        messages.error(request, "Une erreur est survenue lors de la modification de la session de coaching.")
        return redirect('therapeutic_activities:participation_list')

def social_report_detail(request, participation_pk):
    try:
        participation = get_object_or_404(Participation, pk=participation_pk)
        report = get_object_or_404(SocialReport, participation=participation)
        
        context = {
            'page_title': f'Rapport social - {participation.patient}',
            'report': report,
            'participation': participation,
        }
        return render(request, 'social_report_detail.html', context)
    except Exception as e:
        logger.error(f"Erreur dans social_report_detail: {e}")
        messages.error(request, "Une erreur est survenue lors du chargement du rapport social.")
        return redirect('therapeutic_activities:participation_list')

def social_report_edit(request, participation_pk):
    try:
        participation = get_object_or_404(Participation, pk=participation_pk)
        report = get_object_or_404(SocialReport, participation=participation)
        
        if request.method == 'POST':
            form = SocialReportForm(request.POST, instance=report)
            if form.is_valid():
                report = form.save()
                messages.success(request, 'Rapport social modifié avec succès.')
                return redirect('therapeutic_activities:social_report_list')
            else:
                messages.error(request, 'Erreur lors de la modification du rapport social.')
        else:
            form = SocialReportForm(instance=report)
        
        context = {
            'page_title': f'Modifier le rapport social - {participation.patient}',
            'form': form,
            'participation': participation,
            'report': report,
        }
        return render(request, 'social_report_form.html', context)
    except Exception as e:
        logger.error(f"Erreur dans social_report_edit: {e}")
        messages.error(request, "Une erreur est survenue lors de la modification du rapport social.")
        return redirect('therapeutic_activities:participation_list')

# ========================================
# VUES DE STATISTIQUES ET RAPPORTS
# ========================================

def statistics_dashboard(request):
    try:
        # Statistiques générales
        total_activities = Activity.objects.filter(is_active=True).count()
        total_sessions = Session.objects.count()
        total_participations = Participation.objects.count()
        
        # Sessions par statut
        sessions_by_status = Session.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # Participations par statut
        participations_by_status = Participation.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # Top activités
        top_activities = Activity.objects.annotate(
            sessions_count=Count('sessions'),
            participants_count=Count('sessions__participants')
        ).filter(is_active=True).order_by('-participants_count')[:10]
        
        # Top coaches
        top_coaches = Activity.objects.values('coach__full_name').annotate(
            sessions_count=Count('sessions'),
            participants_count=Count('sessions__participants')
        ).filter(coach__isnull=False).order_by('-participants_count')[:10]
        
        # Sessions par mois (6 derniers mois)
        from datetime import datetime, timedelta
        import calendar
        
        monthly_stats = []
        for i in range(6):
            date = timezone.now().date() - timedelta(days=30*i)
            month_start = date.replace(day=1)
            month_end = date.replace(day=calendar.monthrange(date.year, date.month)[1])
            
            sessions_count = Session.objects.filter(
                date__range=[month_start, month_end]
            ).count()
            
            participations_count = Participation.objects.filter(
                session__date__range=[month_start, month_end]
            ).count()
            
            monthly_stats.append({
                'month': month_start.strftime('%B %Y'),
                'sessions': sessions_count,
                'participations': participations_count
            })
        
        monthly_stats.reverse()
        
        context = {
            'page_title': 'Tableau de bord - Statistiques',
            'total_activities': total_activities,
            'total_sessions': total_sessions,
            'total_participations': total_participations,
            'sessions_by_status': sessions_by_status,
            'participations_by_status': participations_by_status,
            'top_activities': top_activities,
            'top_coaches': top_coaches,
            'monthly_stats': monthly_stats,
        }
        return render(request, 'statistics_dashboard.html', context)
    except Exception as e:
        logger.error(f"Erreur dans statistics_dashboard: {e}")
        messages.error(request, "Une erreur est survenue lors du chargement des statistiques.")
        return render(request, 'statistics_dashboard.html', {})

def patient_follow_up(request, patient_id):
    try:
        from apps.patient.models import Patient
        patient = get_object_or_404(Patient, pk=patient_id)
        
        # Participations du patient
        participations = Participation.objects.filter(patient=patient).select_related(
            'session__activity', 'session__location'
        ).order_by('-session__date', '-session__start_time')
        
        # Statistiques du patient
        total_participations = participations.count()
        present_count = participations.filter(status='present').count()
        absent_count = participations.filter(status='absent').count()
        excused_count = participations.filter(status='excused').count()
        
        # Évaluations spécialisées
        evaluations = ErgotherapyEvaluation.objects.filter(participation__patient=patient)
        coaching_sessions = CoachingSession.objects.filter(participation__patient=patient)
        social_reports = SocialReport.objects.filter(participation__patient=patient)
        
        # Progression des scores (si disponible)
        score_progression = []
        for eval in evaluations.order_by('evaluation_date'):
            if eval.rosenberg_score is not None or eval.moca_score is not None:
                score_progression.append({
                    'date': eval.evaluation_date,
                    'rosenberg': eval.rosenberg_score,
                    'moca': eval.moca_score
                })
        
        context = {
            'page_title': f'Suivi patient - {patient}',
            'patient': patient,
            'participations': participations,
            'total_participations': total_participations,
            'present_count': present_count,
            'absent_count': absent_count,
            'excused_count': excused_count,
            'evaluations': evaluations,
            'coaching_sessions': coaching_sessions,
            'social_reports': social_reports,
            'score_progression': score_progression,
        }
        return render(request, 'patient_follow_up.html', context)
    except Exception as e:
        logger.error(f"Erreur dans patient_follow_up: {e}")
        messages.error(request, "Une erreur est survenue lors du chargement du suivi patient.")
        return redirect('therapeutic_activities:participation_list')

def activity_type_report(request, activity_type_id):    
    try:
        activity_type = get_object_or_404(ActivityType, pk=activity_type_id)
        
        # Activités de ce type
        activities = Activity.objects.filter(type=activity_type, is_active=True)
        
        # Sessions de ces activités
        sessions = Session.objects.filter(activity__type=activity_type)
        
        # Participations
        participations = Participation.objects.filter(session__activity__type=activity_type)
        
        # Statistiques
        total_sessions = sessions.count()
        total_participations = participations.count()
        present_count = participations.filter(status='present').count()
        absent_count = participations.filter(status='absent').count()
        excused_count = participations.filter(status='excused').count()
        
        # Sessions par mois
        from datetime import datetime, timedelta
        import calendar
        
        monthly_stats = []
        for i in range(6):
            date = timezone.now().date() - timedelta(days=30*i)
            month_start = date.replace(day=1)
            month_end = date.replace(day=calendar.monthrange(date.year, date.month)[1])
            
            sessions_count = sessions.filter(date__range=[month_start, month_end]).count()
            participations_count = participations.filter(
                session__date__range=[month_start, month_end]
            ).count()
            
            monthly_stats.append({
                'month': month_start.strftime('%B %Y'),
                'sessions': sessions_count,
                'participations': participations_count
            })
        
        monthly_stats.reverse()
        
        context = {
            'page_title': f'Rapport - {activity_type.name}',
            'activity_type': activity_type,
            'activities': activities,
            'sessions': sessions.order_by('-date', '-start_time'),
            'total_sessions': total_sessions,
            'total_participations': total_participations,
            'present_count': present_count,
            'absent_count': absent_count,
            'excused_count': excused_count,
            'monthly_stats': monthly_stats,
        }
        return render(request, 'activity_type_report.html', context)
    except Exception as e:
        logger.error(f"Erreur dans activity_type_report: {e}")
        messages.error(request, "Une erreur est survenue lors du chargement du rapport.")
        return redirect('therapeutic_activities:activity_list')

# ========================================
# VUES D'ALERTES ET NOTIFICATIONS
# ========================================

def alerts_dashboard(request):
    try:
        alerts = []
        
        # Sessions sans coach
        sessions_without_coach = Session.objects.filter(
            activity__coach__isnull=True,
            date__gte=timezone.now().date()
        )
        if sessions_without_coach.exists():
            alerts.append({
                'type': 'warning',
                'title': 'Sessions sans coach',
                'message': f'{sessions_without_coach.count()} session(s) sans coach assigné',
                'items': sessions_without_coach
            })
        
        # Sessions complètes
        full_sessions = []
        for session in Session.objects.filter(
            date__gte=timezone.now().date(),
            status='planned'
        ):
            if session.is_full:
                full_sessions.append(session)
        
        if full_sessions:
            alerts.append({
                'type': 'info',
                'title': 'Sessions complètes',
                'message': f'{len(full_sessions)} session(s) complète(s)',
                'items': full_sessions
            })
        
        # Sessions avec peu de participants
        low_participation_sessions = []
        for session in Session.objects.filter(
            date__gte=timezone.now().date(),
            status='planned'
        ):
            if session.participants_count < 3 and session.max_participants > 5:
                low_participation_sessions.append(session)
        
        if low_participation_sessions:
            alerts.append({
                'type': 'warning',
                'title': 'Faible participation',
                'message': f'{len(low_participation_sessions)} session(s) avec peu de participants',
                'items': low_participation_sessions
            })
        
        # Sessions d'aujourd'hui
        today_sessions = Session.objects.filter(
            date=timezone.now().date(),
            status='planned'
        ).order_by('start_time')
        
        context = {
            'page_title': 'Tableau de bord - Alertes',
            'alerts': alerts,
            'today_sessions': today_sessions,
        }
        return render(request, 'alerts_dashboard.html', context)
    except Exception as e:
        logger.error(f"Erreur dans alerts_dashboard: {e}")
        messages.error(request, "Une erreur est survenue lors du chargement des alertes.")
        return render(request, 'alerts_dashboard.html', {})

# ========================================
# VUES UTILITAIRES
# ========================================

def bulk_participation_create(request):
    try:
        if request.method == 'POST':
            form = BulkParticipationForm(request.POST)
            if form.is_valid():
                patients = form.cleaned_data['patients']
                session = form.cleaned_data['session']
                default_status = form.cleaned_data['default_status']
                
                created_count = 0
                with transaction.atomic():
                    for patient in patients:
                        # Vérifier si la participation existe déjà
                        if not Participation.objects.filter(patient=patient, session=session).exists():
                            Participation.objects.create(
                                patient=patient,
                                session=session,
                                status=default_status,
                                notes=form.cleaned_data.get('notes', '')
                            )
                            created_count += 1
                
                messages.success(request, f'{created_count} participation(s) créée(s) avec succès.')
                return redirect('therapeutic_activities:participation_list')
            else:
                messages.error(request, 'Erreur lors de la création des participations.')
        else:
            form = BulkParticipationForm()
        
        # Debug: vérifier les querysets du formulaire
        logger.info(f"Sessions disponibles: {form.fields['session'].queryset.count()}")
        logger.info(f"Patients disponibles: {form.fields['patients'].queryset.count()}")
        for session in form.fields['session'].queryset:
            logger.info(f"  Session: {session.id} - {session.activity.title if session.activity else 'N/A'} - {session.date}")
        for patient in form.fields['patients'].queryset[:3]:
            logger.info(f"  Patient: {patient.id} - {patient.get_full_name()}")
        
        context = {
            'page_title': 'Créer des participations en masse',
            'form': form,
            'sessions': form.fields['session'].queryset,
            'patients': form.fields['patients'].queryset,
        }
        return render(request, 'bulk_participation_form.html', context)
    except Exception as e:
        logger.error(f"Erreur dans bulk_participation_create: {e}")
        messages.error(request, "Une erreur est survenue lors de la création des participations.")
        return redirect('therapeutic_activities:participation_list')

def session_calendar(request):
    try:
        # Récupérer les données pour les filtres
        coaches = Employee.objects.filter(
            id__in=Activity.objects.filter(is_active=True).values_list('coach_id', flat=True).distinct()
        ).order_by('full_name')
        activities = Activity.objects.filter(is_active=True).order_by('title')
        activity_types = ActivityType.objects.filter(is_active=True).order_by('name')
        
        context = {
            'page_title': 'Calendrier des sessions',
            'coaches': coaches,
            'activities': activities,
            'activity_types': activity_types,
        }
        return render(request, 'session_calendar.html', context)
    except Exception as e:
        logger.error(f"Erreur dans session_calendar: {e}")
        messages.error(request, "Une erreur est survenue lors du chargement du calendrier.")
        return render(request, 'session_calendar.html', {})

@require_GET
def api_sessions(request):
    """API endpoint pour fournir les données JSON au FullCalendar"""
    try:
        # Paramètres de filtrage
        start_date = request.GET.get('start')
        end_date = request.GET.get('end')
        coach_id = request.GET.get('coach')
        activity_id = request.GET.get('activity')
        type_id = request.GET.get('type')
        status = request.GET.get('status')
        
        # Base queryset
        sessions = Session.objects.select_related(
            'activity', 'location', 'activity__coach'
        ).prefetch_related('participants')
        
        # Filtrage par plage de dates
        if start_date:
            try:
                start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
                sessions = sessions.filter(date__gte=start_date)
            except ValueError:
                pass
                
        if end_date:
            try:
                end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
                sessions = sessions.filter(date__lte=end_date)
            except ValueError:
                pass
        
        # Filtrage par coach
        if coach_id:
            sessions = sessions.filter(activity__coach_id=coach_id)
            
        # Filtrage par activité
        if activity_id:
            sessions = sessions.filter(activity_id=activity_id)
            
        # Filtrage par type d'activité
        if type_id:
            sessions = sessions.filter(activity__type_id=type_id)
            
        # Filtrage par statut
        if status:
            sessions = sessions.filter(status=status)
        
        # Construire la réponse JSON
        events = []
        for session in sessions:
            # Déterminer la couleur selon le statut
            color_map = {
                'planned': '#007bff',
                'done': '#28a745',
                'canceled': '#dc3545',
            }
            
            # Construire le titre
            title = f"{session.activity.title}"
            if session.location:
                title += f" - {session.location.name}"
            
            # Dates de début et fin
            start_datetime = timezone.make_aware(
                timezone.datetime.combine(session.date, session.start_time)
            )
            end_datetime = timezone.make_aware(
                timezone.datetime.combine(session.date, session.end_time)
            )
            
            events.append({
                'id': session.id,
                'title': title,
                'start': start_datetime.isoformat(),
                'end': end_datetime.isoformat(),
                'color': color_map.get(session.status, '#6c757d'),
                'extendedProps': {
                    'id': session.id,
                    'activity_title': session.activity.title,
                    'activity_id': session.activity.id,
                    'coach_name': str(session.activity.coach) if session.activity.coach else 'Non assigné',
                    'coach_id': session.activity.coach.id if session.activity.coach else None,
                    'location': session.location.name if session.location else 'Non spécifié',
                    'date': session.date.strftime('%d/%m/%Y'),
                    'start_time': session.start_time.strftime('%H:%M'),
                    'end_time': session.end_time.strftime('%H:%M'),
                    'max_participants': session.max_participants,
                    'participants_count': session.participants.filter(status__in=['present', 'absent', 'excused']).count(),
                    'status': session.status,
                    'notes': session.notes or '',
                }
            })
        
        return JsonResponse(events, safe=False)
        
    except Exception as e:
        logger.error(f"Erreur dans api_sessions: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@require_GET
def api_activity_coaches(request, activity_id):
    """API endpoint pour obtenir les coaches d'une activité"""
    try:
        activity = get_object_or_404(Activity, pk=activity_id)
        coaches = []
        
        if activity.coach:
            coaches.append({
                'id': activity.coach.id,
                'name': activity.coach.get_full_name() or activity.coach.username
            })
        
        return JsonResponse({'coaches': coaches})
        
    except Exception as e:
        logger.error(f"Erreur dans api_activity_coaches: {e}")
        return JsonResponse({'error': str(e)}, status=500)


# ========================================
# VUES LISTES ERGOTHERAPIE
# ========================================

@login_required
def ergotherapy_evaluation_list(request):
    """Liste des évaluations ergothérapiques"""
    try:
        # Gestion des requêtes POST (modification)
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'edit':
                evaluation_id = request.POST.get('evaluation_id')
                try:
                    evaluation = get_object_or_404(ErgotherapyEvaluation, id=evaluation_id)
                    
                    # Mettre à jour les champs
                    evaluation.moca_score = request.POST.get('moca_score') or None
                    evaluation.rosenberg_score = request.POST.get('rosenberg_score') or None
                    evaluation.osa_result = request.POST.get('osa_result', '')
                    evaluation.goals = request.POST.get('goals', '')
                    
                    # Convertir les scores en float si fournis
                    if evaluation.moca_score:
                        evaluation.moca_score = float(evaluation.moca_score)
                    if evaluation.rosenberg_score:
                        evaluation.rosenberg_score = float(evaluation.rosenberg_score)
                    
                    evaluation.save()
                    messages.success(request, "Évaluation modifiée avec succès.")
                    
                except ValueError as ve:
                    messages.error(request, "Erreur dans les valeurs saisies. Vérifiez les scores.")
                except Exception as e:
                    logger.error(f"Erreur lors de la modification de l'évaluation {evaluation_id}: {e}")
                    messages.error(request, "Erreur lors de la modification de l'évaluation.")
                
                return redirect('therapeutic_activities:ergotherapy_evaluation_list')
        
        # Récupérer toutes les évaluations
        evaluations = ErgotherapyEvaluation.objects.select_related(
            'participation__patient', 
            'participation__session__activity',
            'participation__session__location'
        ).order_by('-evaluation_date')
        
        # Recherche
        search_query = request.GET.get('q', '').strip()
        if search_query:
            evaluations = evaluations.filter(
                Q(participation__patient__first_name__icontains=search_query) |
                Q(participation__patient__last_name__icontains=search_query) |
                Q(participation__session__activity__title__icontains=search_query) |
                Q(goals__icontains=search_query)
            )
        
        # Pagination
        paginator = Paginator(evaluations, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Récupérer la liste des patients pour les formulaires
        patients = Patient.objects.all().order_by('last_name', 'first_name')
        
        context = {
            'page_title': 'Évaluations Ergothérapiques',
            'evaluations': page_obj,
            'patients': patients,
            'search_query': search_query,
        }
        
        return render(request, 'ergotherapy_evaluation_list.html', context)
        
    except Exception as e:
        logger.error(f"Erreur dans ergotherapy_evaluation_list: {e}")
        messages.error(request, "Erreur lors du chargement des évaluations.")
        return redirect('therapeutic_activities:activities_home')

@login_required
def coaching_session_list(request):
    """Liste des sessions de coaching"""
    try:
        # Gestion des requêtes POST (création et modification)
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'create':
                try:
                    # Récupérer le patient sélectionné
                    patient_id = request.POST.get('patient')
                    if not patient_id:
                        messages.error(request, "Veuillez sélectionner un patient.")
                        return redirect('therapeutic_activities:coaching_session_list')
                    
                    patient = get_object_or_404(Patient, id=patient_id)
                    
                    # Trouver une participation existante pour ce patient
                    participation = Participation.objects.filter(patient=patient).first()
                    if not participation:
                        messages.error(request, "Aucune participation trouvée pour ce patient.")
                        return redirect('therapeutic_activities:coaching_session_list')
                    
                    # Vérifier qu'il n'y a pas déjà de session de coaching pour cette participation
                    if CoachingSession.objects.filter(participation=participation).exists():
                        messages.warning(request, "Une session de coaching existe déjà pour ce patient.")
                        return redirect('therapeutic_activities:coaching_session_list')
                    
                    # Créer la session de coaching
                    coaching = CoachingSession.objects.create(
                        participation=participation,
                        plan=request.POST.get('plan', ''),
                        result=request.POST.get('result', '')
                    )
                    
                    messages.success(request, "Session de coaching créée avec succès.")
                    return redirect('therapeutic_activities:coaching_session_list')
                    
                except Exception as e:
                    logger.error(f"Erreur lors de la création de la session: {e}")
                    messages.error(request, "Erreur lors de la création de la session de coaching.")
                    return redirect('therapeutic_activities:coaching_session_list')
            
            elif action == 'edit':
                try:
                    coaching_id = request.POST.get('coaching_id')
                    coaching = get_object_or_404(CoachingSession, id=coaching_id)
                    
                    # Mettre à jour les champs
                    coaching.plan = request.POST.get('plan', '')
                    coaching.result = request.POST.get('result', '')
                    coaching.save()
                    
                    messages.success(request, "Session de coaching modifiée avec succès.")
                    return redirect('therapeutic_activities:coaching_session_list')
                    
                except Exception as e:
                    logger.error(f"Erreur lors de la modification de la session {coaching_id}: {e}")
                    messages.error(request, "Erreur lors de la modification de la session de coaching.")
                    return redirect('therapeutic_activities:coaching_session_list')
        
        # Récupérer toutes les sessions de coaching
        coaching_sessions = CoachingSession.objects.select_related(
            'participation__patient',
            'participation__session__activity',
            'participation__session__location'
        ).order_by('-session_date')
        
        # Recherche
        search_query = request.GET.get('q', '').strip()
        if search_query:
            coaching_sessions = coaching_sessions.filter(
                Q(participation__patient__first_name__icontains=search_query) |
                Q(participation__patient__last_name__icontains=search_query) |
                Q(participation__session__activity__title__icontains=search_query) |
                Q(plan__icontains=search_query) |
                Q(result__icontains=search_query)
            )
        
        # Pagination
        paginator = Paginator(coaching_sessions, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Récupérer la liste des patients pour les formulaires
        patients = Patient.objects.all().order_by('last_name', 'first_name')
        
        context = {
            'page_title': 'Sessions de Coaching',
            'coaching_sessions': page_obj,
            'patients': patients,
            'search_query': search_query,
        }
        
        return render(request, 'coaching_session_list.html', context)
        
    except Exception as e:
        logger.error(f"Erreur dans coaching_session_list: {e}")
        messages.error(request, "Erreur lors du chargement des sessions de coaching.")
        return redirect('therapeutic_activities:activities_home')

@login_required  
def social_report_list(request):
    """Liste des rapports sociaux"""
    try:
        # Gestion des requêtes POST (création et modification)
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'create':
                try:
                    # Récupérer le patient sélectionné
                    patient_id = request.POST.get('patient')
                    if not patient_id:
                        messages.error(request, "Veuillez sélectionner un patient.")
                        return redirect('therapeutic_activities:social_report_list')
                    
                    patient = get_object_or_404(Patient, id=patient_id)
                    
                    # Trouver une participation existante pour ce patient
                    participation = Participation.objects.filter(patient=patient).first()
                    if not participation:
                        messages.error(request, "Aucune participation trouvée pour ce patient.")
                        return redirect('therapeutic_activities:social_report_list')
                    
                    # Vérifier qu'il n'y a pas déjà de rapport social pour cette participation
                    if SocialReport.objects.filter(participation=participation).exists():
                        messages.warning(request, "Un rapport social existe déjà pour ce patient.")
                        return redirect('therapeutic_activities:social_report_list')
                    
                    # Créer le rapport social
                    report = SocialReport.objects.create(
                        participation=participation,
                        intervention_plan=request.POST.get('intervention_plan', ''),
                        interview_notes=request.POST.get('interview_notes', ''),
                        exit_summary=request.POST.get('exit_summary', ''),
                        meeting_notes=request.POST.get('meeting_notes', '')
                    )
                    
                    messages.success(request, "Rapport social créé avec succès.")
                    return redirect('therapeutic_activities:social_report_list')
                    
                except Exception as e:
                    logger.error(f"Erreur lors de la création du rapport: {e}")
                    messages.error(request, "Erreur lors de la création du rapport social.")
                    return redirect('therapeutic_activities:social_report_list')
            
            elif action == 'edit':
                try:
                    report_id = request.POST.get('report_id')
                    report = get_object_or_404(SocialReport, id=report_id)
                    
                    # Mettre à jour les champs
                    report.intervention_plan = request.POST.get('intervention_plan', '')
                    report.interview_notes = request.POST.get('interview_notes', '')
                    report.exit_summary = request.POST.get('exit_summary', '')
                    report.meeting_notes = request.POST.get('meeting_notes', '')
                    report.save()
                    
                    messages.success(request, "Rapport social modifié avec succès.")
                    return redirect('therapeutic_activities:social_report_list')
                    
                except Exception as e:
                    logger.error(f"Erreur lors de la modification du rapport {report_id}: {e}")
                    messages.error(request, "Erreur lors de la modification du rapport social.")
                    return redirect('therapeutic_activities:social_report_list')
        
        # Récupérer tous les rapports sociaux
        social_reports = SocialReport.objects.select_related(
            'participation__patient',
            'participation__session__activity', 
            'participation__session__location'
        ).order_by('-report_date')
        
        # Recherche
        search_query = request.GET.get('q', '').strip()
        if search_query:
            social_reports = social_reports.filter(
                Q(participation__patient__first_name__icontains=search_query) |
                Q(participation__patient__last_name__icontains=search_query) |
                Q(participation__session__activity__title__icontains=search_query) |
                Q(intervention_plan__icontains=search_query) |
                Q(interview_notes__icontains=search_query)
            )
        
        # Pagination
        paginator = Paginator(social_reports, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Récupérer la liste des patients pour les formulaires
        patients = Patient.objects.all().order_by('last_name', 'first_name')
        
        context = {
            'page_title': 'Rapports Sociaux',
            'social_reports': page_obj,
            'patients': patients,
            'search_query': search_query,
        }
        
        return render(request, 'social_report_list.html', context)
        
    except Exception as e:
        logger.error(f"Erreur dans social_report_list: {e}")
        messages.error(request, "Erreur lors du chargement des rapports sociaux.")
        return redirect('therapeutic_activities:activities_home')

# ========================================
# VUES STANDALONE POUR CRÉATION D'ÉVALUATIONS
# ========================================

@login_required
def ergotherapy_evaluation_create_standalone(request):
    """Vue standalone pour créer une évaluation ergothérapique sans participation préalable"""
    try:
        if request.method == 'POST':
            try:
                # Récupérer le patient sélectionné
                patient_id = request.POST.get('patient')
                if not patient_id:
                    messages.error(request, "Veuillez sélectionner un patient.")
                    return redirect('therapeutic_activities:ergotherapy_evaluation_list')
                
                patient = get_object_or_404(Patient, id=patient_id)
                
                # Créer une participation temporaire ou utiliser une existante
                # Pour simplifier, on crée une évaluation directement liée à une participation existante
                participation = Participation.objects.filter(patient=patient).first()
                if not participation:
                    messages.error(request, "Aucune participation trouvée pour ce patient.")
                    return redirect('therapeutic_activities:ergotherapy_evaluation_list')
                
                # Vérifier qu'il n'y a pas déjà d'évaluation pour cette participation
                if ErgotherapyEvaluation.objects.filter(participation=participation).exists():
                    messages.warning(request, "Une évaluation existe déjà pour ce patient.")
                    return redirect('therapeutic_activities:ergotherapy_evaluation_list')
                
                # Créer l'évaluation directement
                evaluation = ErgotherapyEvaluation.objects.create(
                    participation=participation,
                    moca_score=float(request.POST.get('moca_score')) if request.POST.get('moca_score') else None,
                    rosenberg_score=float(request.POST.get('rosenberg_score')) if request.POST.get('rosenberg_score') else None,
                    osa_result=request.POST.get('osa_result', ''),
                    goals=request.POST.get('goals', '')
                )
                
                messages.success(request, "Évaluation ergothérapique créée avec succès.")
                return redirect('therapeutic_activities:ergotherapy_evaluation_list')
                
            except ValueError:
                messages.error(request, "Erreur dans les valeurs saisies. Vérifiez les scores.")
                return redirect('therapeutic_activities:ergotherapy_evaluation_list')
            except Exception as e:
                logger.error(f"Erreur lors de la création: {e}")
                messages.error(request, "Erreur lors de la création de l'évaluation.")
                return redirect('therapeutic_activities:ergotherapy_evaluation_list')
        else:
            form = ErgotherapyEvaluationForm()
        
        # Récupérer les participations disponibles pour évaluation
        available_participations = Participation.objects.select_related(
            'patient', 'session__activity', 'session__location'
        ).exclude(
            id__in=ErgotherapyEvaluation.objects.values_list('participation_id', flat=True)
        ).order_by('-session__date')
        
        context = {
            'page_title': 'Nouvelle Évaluation Ergothérapique',
            'form': form,
            'available_participations': available_participations,
        }
        return render(request, 'ergotherapy_evaluation_standalone_form.html', context)
        
    except Exception as e:
        logger.error(f"Erreur dans ergotherapy_evaluation_create_standalone: {e}")
        messages.error(request, "Une erreur est survenue lors de la création de l'évaluation.")
        return redirect('therapeutic_activities:ergotherapy_evaluation_list')

@login_required
def coaching_session_create_standalone(request):
    """Vue standalone pour créer une session de coaching sans participation préalable"""
    try:
        if request.method == 'POST':
            participation_id = request.POST.get('participation_id')
            if not participation_id:
                messages.error(request, "Veuillez sélectionner une participation.")
                return redirect('therapeutic_activities:coaching_session_create')
            
            participation = get_object_or_404(Participation, id=participation_id)
            
            if CoachingSession.objects.filter(participation=participation).exists():
                messages.warning(request, "Une session de coaching existe déjà pour cette participation.")
                return redirect('therapeutic_activities:coaching_session_list')
            
            form = CoachingSessionForm(request.POST)
            if form.is_valid():
                coaching = form.save(commit=False)
                coaching.participation = participation
                coaching.coach = request.user
                coaching.save()
                messages.success(request, "Session de coaching créée avec succès.")
                return redirect('therapeutic_activities:coaching_session_list')
        else:
            form = CoachingSessionForm()
        
        available_participations = Participation.objects.select_related(
            'patient', 'session__activity', 'session__location'
        ).exclude(
            id__in=CoachingSession.objects.values_list('participation_id', flat=True)
        ).order_by('-session__date')
        
        context = {
            'page_title': 'Nouvelle Session de Coaching',
            'form': form,
            'available_participations': available_participations,
        }
        return render(request, 'coaching_session_standalone_form.html', context)
        
    except Exception as e:
        logger.error(f"Erreur dans coaching_session_create_standalone: {e}")
        messages.error(request, "Une erreur est survenue lors de la création de la session.")
        return redirect('therapeutic_activities:coaching_session_list')

@login_required
def social_report_create_standalone(request):
    """Vue standalone pour créer un rapport social sans participation préalable"""
    try:
        if request.method == 'POST':
            participation_id = request.POST.get('participation_id')
            if not participation_id:
                messages.error(request, "Veuillez sélectionner une participation.")
                return redirect('therapeutic_activities:social_report_create')
            
            participation = get_object_or_404(Participation, id=participation_id)
            
            if SocialReport.objects.filter(participation=participation).exists():
                messages.warning(request, "Un rapport social existe déjà pour cette participation.")
                return redirect('therapeutic_activities:social_report_list')
            
            form = SocialReportForm(request.POST)
            if form.is_valid():
                report = form.save(commit=False)
                report.participation = participation
                report.social_worker = request.user
                report.save()
                messages.success(request, "Rapport social créé avec succès.")
                return redirect('therapeutic_activities:social_report_list')
        else:
            form = SocialReportForm()
        
        available_participations = Participation.objects.select_related(
            'patient', 'session__activity', 'session__location'
        ).exclude(
            id__in=SocialReport.objects.values_list('participation_id', flat=True)
        ).order_by('-session__date')
        
        context = {
            'page_title': 'Nouveau Rapport Social',
            'form': form,
            'available_participations': available_participations,
        }
        return render(request, 'social_report_standalone_form.html', context)
        
    except Exception as e:
        logger.error(f"Erreur dans social_report_create_standalone: {e}")
        messages.error(request, "Une erreur est survenue lors de la création du rapport.")
        return redirect('therapeutic_activities:social_report_list')