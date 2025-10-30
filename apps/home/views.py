import logging
import json
from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from apps.home.models import User, UserPermission, AuditLog
from apps.hr.models.employee import Employee
from apps.home.forms import UserForm
from django.views import View
from django.apps import apps as django_apps
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate, login as auth_login
from django.urls import resolve, Resolver404
from django.contrib.contenttypes.models import ContentType
try:
    from weasyprint import HTML
except Exception:  # WeasyPrint optional during checks/migrations
    HTML = None
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, time
from django.utils.dateparse import parse_date, parse_time
from apps.home.utils import log_action
from functools import wraps
from django.shortcuts import redirect
from django.http import JsonResponse
import logging
from django.contrib.sessions.models import Session
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models.functions import TruncMonth, TruncDay
import json
logger = logging.getLogger(__name__)
apps_urls = {
    'reception': '/reception/',
    'consultation': '/patient/consultation/',
    'billing': '/billing/',
    'hospitalization': '/hospitalization/',
    'pharmacy': '/pharmacy/',
    'therapeutic_activities': '/therapeutic_activities/',
    'recruitment': '/recruitment/',
    'purchases': '/purchases/',
    'stock_moves': '/inventory/stock-moves/',
    'inventory': '/inventory/',
    'restaurant': '/restaurant/',
    'hr': '/hr/',
    'maintenance': '/maintenance/',
    'patient': '/patient/',
    'user_list': '/users/',
    'audit_log': '/audit-logs/',
    'formation': '/formation/',
    'hosting': '/hosting/',
}

def unauthorized(request):
    """Simple page for unauthorized access."""
    return render(request, 'not_found.html', status=403)

def login_view(request):
    """
    Vue de connexion avec nettoyage préalable des sessions
    """
    # Nettoyer toute session existante avant la connexion
    if request.method == 'GET':
        if request.user.is_authenticated or request.session.get('user'):
            auth_logout(request)
            request.session.flush()
    
    if request.method == 'POST':
        # Nettoyer la session avant toute tentative de connexion
        auth_logout(request)
        request.session.flush()
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            return JsonResponse({
                'success': False, 
                'message': 'Nom d\'utilisateur et mot de passe requis.'
            })
        
        user = authenticate(request, username=username, password=password)
        if user:
            # Vérifier que l'utilisateur est actif
            if not user.is_activated:
                logger.warning(f"Inactive user {username} attempted login")
                return JsonResponse({
                    'success': False, 
                    'message': 'Compte désactivé. Contactez l\'administrateur.'
                })
            
            # Connexion de l'utilisateur Django
            auth_login(request, user)
            
            # Construction des permissions
            permissions = {}
            installed_apps = [
                app_config.name for app_config in django_apps.get_app_configs() 
                if app_config.name.startswith('apps.')
            ]
            
            # Si l'utilisateur est superuser, donner toutes les permissions
            if user.is_superuser:
                for app_name in installed_apps:
                    app_key = app_name.split('.')[-1]
                    permissions[app_key] = {
                        'read': True,
                        'write': True,
                        'update': True,
                        'delete': True,
                    }
            else:
                for app_name in installed_apps:
                    app_key = app_name.split('.')[-1]
                    perm = user.permissions.filter(app_name=app_name).first()
                    permissions[app_key] = {
                        'read': perm.can_read if perm else False,
                        'write': perm.can_write if perm else False,
                        'update': perm.can_update if perm else False,
                        'delete': perm.can_delete if perm else False,
                    }
            
            # Déterminer le statut HR et superviseur
            hr_is_supervisor = False
            is_hr_employee = False
            is_supervisor = False
            if user.employee:
                emp = user.employee
                if emp.is_supervisor:
                    is_supervisor = True
                if (emp.department and emp.department.name and 
                    emp.department.name.lower().startswith('ressources humaines')):
                    is_hr_employee = True
                    if emp.is_supervisor:
                        hr_is_supervisor = True

            # Créer la session utilisateur
            request.session['user'] = {
                'id': user.pk,
                'nom': user.nom,
                'prenom': user.prenom,
                'username': user.username,
                'is_activated': user.is_activated,
                'employee': user.employee.pk if user.employee else None,
                'permissions': permissions,
                'hr_is_supervisor': hr_is_supervisor,
                'is_hr_employee': is_hr_employee,
                'is_supervisor': is_supervisor,
                'can_leave_approve': (is_hr_employee or is_supervisor),
                'login_time': timezone.now().isoformat(),  # Timestamp de connexion
            }
            
            # Forcer la sauvegarde de la session
            request.session.modified = True
            
            logger.info(f"User {username} logged in successfully at {timezone.now()}")
            
            return JsonResponse({'success': True, 'redirect': '/welcome/'})
        else:
            logger.warning(f"Login failed for username: {username}")
            return JsonResponse({
                'success': False, 
                'message': 'Nom d\'utilisateur ou mot de passe incorrect.'
            })
    
    # GET request - afficher la page de connexion
    context = {
        'page_title': 'Connexion - Oralys ERP Clinique',
    }
    return render(request, 'login.html', context)



def logout_view(request):
    """
    Déconnexion ultime avec nettoyage complet de toutes les sessions
    """
    try:
        # Capturer les informations avant nettoyage
        username = "Unknown"
        user_id = None
        
        if request.session.get('user'):
            username = request.session.get('user', {}).get('username', 'Unknown')
            user_id = request.session.get('user', {}).get('id')
        elif hasattr(request, 'user') and request.user.is_authenticated:
            username = request.user.username
            user_id = request.user.pk

        logger.info(f"Logout initiated for user: {username} (ID: {user_id})")

        # 1. Nettoyer TOUTES les sessions de cet utilisateur
        if user_id:
            try:
                with transaction.atomic():
                    # Trouver toutes les sessions qui contiennent cet utilisateur
                    all_sessions = Session.objects.all()
                    for session in all_sessions:
                        try:
                            session_data = session.get_decoded()
                            if session_data.get('user', {}).get('id') == user_id:
                                session.delete()
                                logger.debug(f"Deleted session {session.session_key} for user {user_id}")
                        except:
                            # Si on ne peut pas décoder, supprimer par sécurité
                            session.delete()
            except Exception as e:
                logger.error(f"Error cleaning user sessions: {e}")

        # 2. Déconnexion Django
        auth_logout(request)
        
        # 3. Nettoyage de la session courante
        current_session_key = request.session.session_key
        request.session.flush()
        
        # 4. Supprimer explicitement la session courante de la DB
        if current_session_key:
            try:
                Session.objects.filter(session_key=current_session_key).delete()
            except:
                pass

        # 5. Créer la réponse avec nettoyage des cookies
        response = redirect('login')
        
        # 6. Supprimer tous les cookies liés à la session
        cookies_to_delete = ['sessionid', 'csrftoken', 'messages']
        for cookie_name in cookies_to_delete:
            response.delete_cookie(cookie_name)
            response.delete_cookie(cookie_name, domain=request.get_host())
            response.delete_cookie(cookie_name, path='/')

        # 7. Headers de sécurité maximale
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        response['Clear-Site-Data'] = '"cache", "cookies", "storage"'
        
        logger.info(f"Complete logout successful for user: {username}")
        
        return response
        
    except Exception as e:
        logger.error(f"Critical error during logout: {str(e)}", exc_info=True)
        # En cas d'erreur critique, forcer quand même le nettoyage
        try:
            auth_logout(request)
            request.session.flush()
        except:
            pass
        
        response = redirect('login')
        response.delete_cookie('sessionid')
        response.delete_cookie('csrftoken')
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

def welcome_view(request):
    """
    Vue welcome avec vérification stricte de la session
    """
    # VERIFICATION STRICTE - Ne pas faire confiance au middleware
    session_user = request.session.get('user')
    
    if not session_user:
        logger.warning("Welcome access without session user - redirecting to login")
        if hasattr(request, 'user') and request.user.is_authenticated:
            auth_logout(request)
        request.session.flush()
        return redirect('login')
    
    # Vérifier que l'utilisateur existe en base et est actif
    try:
        user_obj = User.objects.get(pk=session_user.get('id'))
        if not user_obj.is_activated:
            logger.warning(f"Inactive user {user_obj.username} accessing welcome")
            auth_logout(request)
            request.session.flush()
            return redirect('login')
    except User.DoesNotExist:
        logger.warning(f"User {session_user.get('id')} not found - redirecting to login")
        auth_logout(request)
        request.session.flush()
        return redirect('login')
    
    # Vérification de cohérence avec Django auth
    if hasattr(request, 'user') and request.user.is_authenticated:
        if request.user.pk != session_user.get('id'):
            logger.warning(f"User mismatch in welcome: Django={request.user.pk}, Session={session_user.get('id')}")
            auth_logout(request)
            request.session.flush()
            return redirect('login')
    
    # Reste du code existant...
    user = request.session.get('user')
    authorized_apps = []
    
    installed_apps = [
        app_config.name for app_config in django_apps.get_app_configs()
        if app_config.name.startswith('apps.')
    ]
    
    
    apps_icons = {
        'reception': 'fas fa-door-open',
        'consultation': 'fas fa-calendar-check',
        'billing': 'fas fa-file-invoice-dollar',
        'hospitalization': 'fas fa-procedures',
        'pharmacy': 'fas fa-pills',
        'therapeutic_activities': 'fa-solid fa-bomb',
        'recruitment': 'fas fa-user-plus',
        'orders': 'fas fa-shopping-cart',
        'purchases': 'fas fa-shopping-cart',
        'stock_moves': 'fas fa-boxes',
        'inventory': 'fas fa-boxes',
        'Restauration': 'fas fa-utensils',
        'hr': 'fas fa-users',
        'maintenance': 'fas fa-tools',
        'demandes': 'fas fa-clipboard-list',
        'patient': 'fas fa-user-injured',
        'home': 'fas fa-user-cog',
        'user_list': 'fas fa-user-cog',
        'formation': 'fas fa-graduation-cap',
        'parcauto': 'fas fa-car',
        'audit_log': 'fas fa-history',
        'hosting': 'fas fa-hotel'
    }
    
    apps_urls = {
        'reception': '/reception/',
        'consultation': '/patient/consultation/',
        'billing': '/billing/',
        'hospitalization': '/hospitalization/',
        'pharmacy': '/pharmacy/',
        'therapeutic_activities': '/therapeutic_activities/',
        'recruitment': '/recruitment/',
        'purchases': '/purchases/',
        'stock_moves': '/inventory/stock-moves/',
        'inventory': '/inventory/products/',
        'Restauration': '/restauration/',
        'hr': '/hr/',
        'maintenance': '/maintenance/',
        'demandes': '/demandes/',
        'patient': '/patient/',
        'formation': '/formation/',
        'audit_log': '/audit-logs/',
        'parcauto': '/parcauto/',
        'hosting': '/hosting/'
    }
    
    apps_labels = {
        'reception': 'Accueil et Réception',
        'consultation': 'Consultation',
        'billing': 'Facturation & Assurances',
        'hospitalization': 'Hébergement',
        'products': 'Pharmacie (Produits)',
        'pharmacy': 'Pharmacie',
        'therapeutic_activities': 'activites therapeutiques',
        'recruitment': 'Recrutement',
        'orders': 'Achats & Fournisseurs (Commandes)',
        'purchases': 'Achats & Fournisseurs',
        'stock_moves': 'Stock & Logistique (Mouvements)',
        'inventory': 'Stock & Logistique',
        'Restauration': 'Restauration',
        'hr': 'Ressources Humaines',
        'maintenance': 'Maintenance',
        'demandes': 'Demandes',
        'patient': 'Patients',
        'user_management_dashboard': 'Gestion des Utilisateurs',
        'formation': 'Formation',
        'audit_log': 'Journaux d\'Audit',
        'parcauto': 'ParKing',
        'hosting': 'Hébergement'
    }
    
    # Utiliser l'objet user de la base au lieu de la session
    is_superuser = user_obj.is_superuser
    
    for app_name in installed_apps:
        app_label = app_name.split('.')[-1]
        permissions = user.get('permissions', {}).get(app_label, {})
        
        if is_superuser or permissions.get('read', False):
            try:
                app_config = django_apps.get_app_config(app_label)
                label = apps_labels.get(app_label, app_config.verbose_name or app_label.capitalize())
            except:
                # Si l'app n'existe pas, utiliser les valeurs par défaut
                label = apps_labels.get(app_label, app_label.capitalize())
            
            icon = apps_icons.get(app_label, 'fas fa-question')
            url = apps_urls.get(app_label, f"/{app_label}/")

            if app_label == 'hr' and not user.get('is_hr_employee', False):
                url = '/hr/leaves/'
            
            if app_label == 'home':
                url = apps_urls.get('user_management_dashboard', '/user/management/dashboard/')
                label = apps_labels.get('user_management_dashboard', 'Gestion des Utilisateurs')
                icon = apps_icons.get('user_management_dashboard', 'fas fa-user-cog')
                try:
                    url = reverse('user_management_dashboard')
                except:
                    logger.warning(f"Could not reverse 'user_management_dashboard', using fallback: {url}")

            authorized_apps.append((app_label, label, url, icon))
    
    logger.debug(f"Welcome view loaded for user {user['username']} with {len(authorized_apps)} apps")
    
    context = {
        'page_title': 'Bienvenue - Oralys ERP Clinique',
        'user': user,
        'authorized_apps': authorized_apps,
    }
    
    return render(request, 'welcome.html', context)


logger = logging.getLogger(__name__)

def require_session_user(view_func):
    """
    Décorateur qui force la vérification stricte de la session
    Utiliser sur toutes les vues qui nécessitent une authentification
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Vérification stricte de la session
        session_user = request.session.get('user')
        
        if not session_user:
            logger.warning(f"Access denied to {view_func.__name__}: No session user")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Session expired', 'redirect': '/login/'}, status=403)
            
            # Nettoyer complètement
            if hasattr(request, 'user') and request.user.is_authenticated:
                auth_logout(request)
            request.session.flush()
            return redirect('login')
        
        # Vérifier que l'utilisateur existe en base
        try:
            user_obj = User.objects.get(pk=session_user.get('id'))
            if not user_obj.is_activated:
                logger.warning(f"Access denied to {view_func.__name__}: User {user_obj.username} is inactive")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'Account disabled', 'redirect': '/login/'}, status=403)
                
                auth_logout(request)
                request.session.flush()
                return redirect('login')
        except User.DoesNotExist:
            logger.warning(f"Access denied to {view_func.__name__}: User {session_user.get('id')} not found")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'User not found', 'redirect': '/login/'}, status=403)
            
            auth_logout(request)
            request.session.flush()
            return redirect('login')
        
        # Vérification de cohérence Django/Session
        if hasattr(request, 'user') and request.user.is_authenticated:
            if request.user.pk != session_user.get('id'):
                logger.warning(f"Access denied to {view_func.__name__}: User ID mismatch")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'Session invalid', 'redirect': '/login/'}, status=403)
                
                auth_logout(request)
                request.session.flush()
                return redirect('login')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper

def require_session_user_json(view_func):
    """
    Version pour les vues qui retournent du JSON
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        session_user = request.session.get('user')
        
        if not session_user:
            logger.warning(f"JSON API access denied to {view_func.__name__}: No session user")
            return JsonResponse({'error': 'Not authenticated', 'redirect': '/login/'}, status=403)
        
        try:
            user_obj = User.objects.get(pk=session_user.get('id'))
            if not user_obj.is_activated:
                logger.warning(f"JSON API access denied to {view_func.__name__}: User inactive")
                return JsonResponse({'error': 'Account disabled', 'redirect': '/login/'}, status=403)
        except User.DoesNotExist:
            logger.warning(f"JSON API access denied to {view_func.__name__}: User not found")
            return JsonResponse({'error': 'User not found', 'redirect': '/login/'}, status=403)
        
        if hasattr(request, 'user') and request.user.is_authenticated:
            if request.user.pk != session_user.get('id'):
                logger.warning(f"JSON API access denied to {view_func.__name__}: User ID mismatch")
                return JsonResponse({'error': 'Session invalid', 'redirect': '/login/'}, status=403)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
class UserListView(TemplateView):
    template_name = 'user_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Gestion des Utilisateurs'
        query = self.request.GET.get('q', '')
        users = User.objects.filter(pk__isnull=False).select_related('employee').order_by('username')
        
        if query:
            users = users.filter(
                Q(username__icontains=query) |
                Q(nom__icontains=query) |
                Q(prenom__icontains=query)
            )
        
        # Add pagination
        paginator = Paginator(users, 10)  # Show 10 users per page
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        context['users'] = page_obj.object_list
        context['page_obj'] = page_obj
        context['employees'] = Employee.objects.all()
        context['form'] = UserForm()
        installed_apps = [
            {'name': app_config.name, 'label': app_config.verbose_name or app_config.name.split('.')[-1].capitalize()}
            for app_config in django_apps.get_app_configs()
            if app_config.name.startswith('apps.')
        ]
        context['apps'] = installed_apps
        return context

    def post(self, request, *args, **kwargs):
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Gestion du mot de passe - hachage approprié
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            
            user.save()
            
            # Traitement des permissions après la création de l'utilisateur
            permissions_data = {}
            for app_name in [app_config.name.split('.')[-1] for app_config in django_apps.get_app_configs() if app_config.name.startswith('apps.')]:
                permissions_data[app_name] = {
                    'read': request.POST.get(f'permissions[{app_name}][read]') == 'on',
                    'write': request.POST.get(f'permissions[{app_name}][write]') == 'on',
                    'update': request.POST.get(f'permissions[{app_name}][update]') == 'on',
                    'delete': request.POST.get(f'permissions[{app_name}][delete]') == 'on',
                }

            # Sauvegarde des permissions
            installed_apps = [
                app_config.name for app_config in django_apps.get_app_configs()
                if app_config.name.startswith('apps.')
            ]
            for app_name in installed_apps:
                app_key = app_name.split('.')[-1]
                perm_data = permissions_data.get(app_key, {'read': False, 'write': False, 'update': False, 'delete': False})

                UserPermission.objects.create(
                    user=user,
                    app_name=app_name,
                    can_read=perm_data['read'],
                    can_write=perm_data['write'],
                    can_update=perm_data['update'],
                    can_delete=perm_data['delete']
                )

            log_action(self.request.user, user, 'creation')
            messages.success(request, "Utilisateur créé avec succès.")
            return redirect('user_list')
        else:
            logger.error(f"Form errors: {form.errors}")
            messages.error(request, "Erreur lors de la création de l'utilisateur. Veuillez vérifier le formulaire.")
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return render(request, self.template_name, context)
@require_session_user
def user_get(request, pk):
    # Vérifie la présence de l'utilisateur en session; sinon, utilise request.user
    if not request.session.get('user'):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Not authenticated'}, status=403)
        else:
            # Reconstruire un dict session minimal pour poursuivre
            request.session['user'] = {
                'id': request.user.pk,
            }
    
    user = get_object_or_404(User, pk=pk)
    permissions = {}
    installed_apps = [
        app_config.name for app_config in django_apps.get_app_configs()
        if app_config.name.startswith('apps.')
    ]
    
    # If user is superuser, grant access to all apps
    if user.is_superuser:
        for app_name in installed_apps:
            app_key = app_name.split('.')[-1]
            permissions[app_key] = {
                'read': True,
                'write': True,
                'update': True,
                'delete': True,
            }
    else:
        for app_name in installed_apps:
            app_key = app_name.split('.')[-1]
            perm = user.permissions.filter(app_name=app_name).first()
            permissions[app_key] = {
                'read': perm.can_read if perm else False,
                'write': perm.can_write if perm else False,
                'update': perm.can_update if perm else False,
                'delete': perm.can_delete if perm else False,
            }
    
    data = {
        'id': user.pk,
        'nom': user.nom,
        'prenom': user.prenom,
        'username': user.username,
        'is_activated': user.is_activated,
        'employee': user.employee.pk if user.employee else None,
        'permissions': permissions,
        'is_superuser': user.is_superuser,
        'is_staff': user.is_staff,
    }
    return JsonResponse(data)

class UserUpdateView(TemplateView):
    def post(self, request, pk):
        if not request.session.get('user'):
            return JsonResponse({'error': 'Not authenticated'}, status=403)

        user = get_object_or_404(User, pk=pk)

        form = UserForm(request.POST, instance=user)

        if form.is_valid():
            form.save() # La logique du mot de passe est maintenant dans le formulaire

            # Traitement des permissions selon la structure de données de la première version
            permissions_data = {}
            for key, value in request.POST.items():
                if key.startswith('permissions['):
                    parts = key.replace('permissions[', '').rstrip(']').split('][')
                    if len(parts) == 2:
                        app, perm = parts
                        if app not in permissions_data:
                            permissions_data[app] = {}
                        permissions_data[app][perm] = value.lower() in ('true', 'on', '1')

            installed_apps = [
                app_config.name for app_config in django_apps.get_app_configs()
                if app_config.name.startswith('apps.')
            ]
            
            for app_name in installed_apps:
                app_key = app_name.split('.')[-1]
                perm_data = permissions_data.get(app_key, {'read': False, 'write': False, 'update': False, 'delete': False})

                perm_obj, created = UserPermission.objects.get_or_create(
                    user=user,
                    app_name=app_name,
                    defaults={
                        'can_read': perm_data.get('read', False),
                        'can_write': perm_data.get('write', False),
                        'can_update': perm_data.get('update', False),
                        'can_delete': perm_data.get('delete', False),
                    }
                )
                if not created:
                    perm_obj.can_read = perm_data.get('read', False)
                    perm_obj.can_write = perm_data.get('write', False)
                    perm_obj.can_update = perm_data.get('update', False)
                    perm_obj.can_delete = perm_data.get('delete', False)
                    perm_obj.save()

            # Si l'utilisateur modifie ses propres permissions, mettre à jour la session
            if request.session['user']['id'] == user.pk:
                permissions = {}
                
                # Si l'utilisateur est superuser, donner toutes les permissions
                if user.is_superuser:
                    for app_name in installed_apps:
                        app_key = app_name.split('.')[-1]
                        permissions[app_key] = {
                            'read': True,
                            'write': True,
                            'update': True,
                            'delete': True,
                        }
                else:
                    for app_name in installed_apps:
                        app_key = app_name.split('.')[-1]
                        perm = user.permissions.filter(app_name=app_name).first()
                        permissions[app_key] = {
                            'read': perm.can_read if perm else False,
                            'write': perm.can_write if perm else False,
                            'update': perm.can_update if perm else False,
                            'delete': perm.can_delete if perm else False,
                        }
                
                # Actualiser les flags HR
                hr_is_supervisor = False
                is_hr_employee = False
                is_supervisor = False

                if user.employee:
                    if user.employee.is_supervisor:
                        is_supervisor = True
                    if user.employee.department and user.employee.department.name.lower().startswith('ressources humaines'):
                        is_hr_employee = True
                        if user.employee.is_supervisor:
                            hr_is_supervisor = True
                
                request.session['user']['hr_is_supervisor'] = hr_is_supervisor
                request.session['user']['is_hr_employee'] = is_hr_employee
                request.session['user']['is_supervisor'] = is_supervisor
                request.session['user']['permissions'] = permissions
                request.session['user']['can_leave_approve'] = (is_hr_employee or is_supervisor)
                request.session.modified = True

            log_action(request.user, user, 'modification')
            return JsonResponse({'success': True})

        else:
            logger.error(f"Update form errors: {form.errors}")
            errors = form.errors.as_data()
            formatted_errors = {field: [str(e) for e in errors[field]] for field in errors}
            return JsonResponse({'success': False, 'errors': formatted_errors}, status=400)

class UserToggleActivationView(TemplateView):
    def get(self, request, pk):
        if not request.session.get('user'):
            return JsonResponse({'error': 'Not authenticated'}, status=403)
        user = get_object_or_404(User, pk=pk)
        user.is_activated = not user.is_activated
        user.save()
        log_action(request.user, user, 'modification')
        status = "activé" if user.is_activated else "désactivé"
        message = f"Utilisateur {user.username} {status} avec succès."
        
        # Si l'utilisateur modifie son propre statut d'activation, mettre à jour la session
        if request.session['user']['id'] == user.pk:
            request.session['user']['is_activated'] = user.is_activated
            permissions = {}
            installed_apps = [app_config.name for app_config in django_apps.get_app_configs() if app_config.name.startswith('apps.')]
            
            # Si l'utilisateur est superuser, donner toutes les permissions
            if user.is_superuser:
                for app_name in installed_apps:
                    app_key = app_name.split('.')[-1]
                    permissions[app_key] = {
                        'read': True,
                        'write': True,
                        'update': True,
                        'delete': True,
                    }
            else:
                for app_name in installed_apps:
                    app_key = app_name.split('.')[-1]
                    perm = user.permissions.filter(app_name=app_name).first()
                    permissions[app_key] = {
                        'read': perm.can_read if perm else False,
                        'write': perm.can_write if perm else False,
                        'update': perm.can_update if perm else False,
                        'delete': perm.can_delete if perm else False,
                    }
            request.session['user']['permissions'] = permissions
            request.session.modified = True
        return JsonResponse({'success': True, 'message': message})

class UserDeleteView(View):
    def post(self, request, pk):
        if not request.session.get('user'):
            return JsonResponse({'error': 'Not authenticated'}, status=403)
        user = get_object_or_404(User, pk=pk)
        username = user.username
        log_action(request.user, user, 'suppression')
        user.delete()
        messages.success(request, f"Utilisateur {username} supprimé avec succès.")
        return redirect('user_list')
@require_session_user_json
def user_table_body(request):
    if not request.session.get('user'):
        return HttpResponse('', status=403)
    query = request.GET.get('q', '')
    page_number = request.GET.get('page', 1)
    users = User.objects.filter(pk__isnull=False).select_related('employee').order_by('username')
    
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(nom__icontains=query) |
            Q(prenom__icontains=query)
        )
    
    # Add pagination
    paginator = Paginator(users, 10)
    page_obj = paginator.get_page(page_number)
    
    logger.debug(f"Filtered users: {list(page_obj.object_list.values('pk', 'username', 'nom', 'prenom', 'employee__full_name'))}")
    return render(request, 'user_table_body.html', {'users': page_obj.object_list, 'page_obj': page_obj})

class RestrictUnauthorizedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Chemins autorisés sans authentification
        allowed_paths = ['/login/', '/logout/', '/not_found/', '/favicon.ico', '/media/', '/essential/']
        requested_path = request.path

        # Permettre l'accès aux chemins autorisés
        if any(requested_path.startswith(path) for path in allowed_paths):
            return self.get_response(request)

        # VERIFICATION STRICTE DE LA SESSION
        # Au lieu de vérifier request.user.is_authenticated, on vérifie directement la session
        session_user = request.session.get('user')
        
        if not session_user:
            logger.warning(f"No session user found for request to {requested_path}")
            # Forcer le nettoyage complet et redirection
            if hasattr(request, 'user'):
                auth_logout(request)
            request.session.flush()
            return redirect('login')

        # Vérifier que l'utilisateur existe toujours en base
        try:
            user_obj = User.objects.get(pk=session_user.get('id'))
            if not user_obj.is_activated:
                logger.warning(f"Inactive user {user_obj.username} attempting access to {requested_path}")
                auth_logout(request)
                request.session.flush()
                return redirect('login')
        except User.DoesNotExist:
            logger.warning(f"User {session_user.get('id')} not found in database")
            auth_logout(request)
            request.session.flush()
            return redirect('login')

        # Vérification supplémentaire : vérifier la cohérence avec Django auth
        if hasattr(request, 'user') and request.user.is_authenticated:
            if request.user.pk != session_user.get('id'):
                logger.warning(f"User ID mismatch: Django={request.user.pk}, Session={session_user.get('id')}")
                auth_logout(request)
                request.session.flush()
                return redirect('login')

        # Autoriser l'accès à /welcome/ après vérifications
        if requested_path == '/welcome/':
            return self.get_response(request)

        # Vérification des permissions pour les autres chemins
        permissions = session_user.get('permissions', {})

        # Bypass HR leave management URLs
        if requested_path.startswith('/hr/leaves/'):
            return self.get_response(request)

        # Vérifier si l'utilisateur est superuser
        is_superuser = user_obj.is_superuser
        
        is_authorized = False
        if is_superuser:
            is_authorized = True
        else:
            # Autoriser directement hosting
            if requested_path.startswith('/hosting/'):
                return self.get_response(request)

            for app_name, url in apps_urls.items():
                if requested_path.startswith(url):
                    app_key = app_name if app_name not in ['user_list', 'audit_log'] else 'home'
                    if permissions.get(app_key, {}).get('read', False):
                        is_authorized = True
                        break

        if not is_authorized:
            logger.warning(f"Unauthorized access attempt by user {session_user['username']} to {requested_path}")
            return render(request, 'not_found.html', {'page_title': 'Page Non Trouvée - Oralys ERP Clinique'}, status=403)

        return self.get_response(request)
def validate_and_clean_session(request):
    """
    Valide la session utilisateur et nettoie si nécessaire
    Retourne True si la session est valide, False sinon
    """
    try:
        # Vérifier si l'utilisateur Django est authentifié
        if not request.user.is_authenticated:
            return False

        # Vérifier la présence de l'utilisateur en session
        session_user = request.session.get('user')
        if not session_user:
            return False

        # Vérifier la cohérence des IDs
        if session_user.get('id') != request.user.pk:
            logger.warning(f"Session ID mismatch: session={session_user.get('id')}, auth={request.user.pk}")
            clean_session(request)
            return False

        # Vérifier que l'utilisateur existe en base et est actif
        try:
            user_obj = User.objects.get(pk=session_user.get('id'))
            if not user_obj.is_activated:
                logger.warning(f"User {user_obj.username} is deactivated")
                clean_session(request)
                return False
        except User.DoesNotExist:
            logger.warning(f"User {session_user.get('id')} not found in database")
            clean_session(request)
            return False

        return True

    except Exception as e:
        logger.error(f"Error validating session: {str(e)}", exc_info=True)
        clean_session(request)
        return False

def clean_session(request):
    """
    Nettoie complètement la session et déconnecte l'utilisateur
    """
    try:
        auth_logout(request)
        request.session.flush()
        
        # Supprimer la session de la base de données
        if hasattr(request, 'session') and request.session.session_key:
            try:
                from django.contrib.sessions.models import Session
                Session.objects.filter(session_key=request.session.session_key).delete()
            except:
                pass
                
    except Exception as e:
        logger.error(f"Error cleaning session: {str(e)}", exc_info=True)

# Décorateur pour protéger les vues
def require_valid_session(view_func):
    """
    Décorateur pour s'assurer qu'une vue a une session valide
    """
    def wrapper(request, *args, **kwargs):
        if not validate_and_clean_session(request):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

class UserResetPasswordView(View):
    def post(self, request, pk):
        if not request.session.get('user'):
            return JsonResponse({'error': 'Not authenticated'}, status=403)
        
        user = get_object_or_404(User, pk=pk)
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password_confirm = request.POST.get('new_password_confirm')
        
        errors = {}
        
        if not authenticate(request, username=user.username, password=old_password):
            errors['old_password'] = ['L\'ancien mot de passe est incorrect.']
        
        if not new_password:
            errors['new_password'] = ['Le nouveau mot de passe est requis.']
        elif len(new_password) < 8:
            errors['new_password'] = ['Le nouveau mot de passe doit contenir au moins 8 caractères.']
        
        if new_password != new_password_confirm:
            errors['new_password_confirm'] = ['Les mots de passe ne correspondent pas.']
        
        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)
        
        user.set_password(new_password)
        user.save()
        logger.debug(f"Password reset for user: pk={user.pk}, username={user.username}")
        
        if request.session['user']['id'] == user.pk:
            request.session['user']['password_updated'] = True
            request.session.modified = True
        
        return JsonResponse({'success': True})

class AuditLogListView(TemplateView):
    template_name = 'audit_log_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Journaux d\'Audit'
        query = self.request.GET.get('q', '')
        action_filter = self.request.GET.get('action', '')
        start_date = self.request.GET.get('start_date', '')
        start_time = self.request.GET.get('start_time', '')
        end_date = self.request.GET.get('end_date', '')
        end_time = self.request.GET.get('end_time', '')

        logs = AuditLog.objects.all().select_related('created_by', 'content_type').order_by('-date_time')

        if query:
            logs = logs.filter(
                Q(entity_name__icontains=query) |
                Q(object_id__icontains=query) |
                Q(created_by__username__icontains=query)
            )

        if action_filter:
            logs = logs.filter(action=action_filter)

        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                start_datetime = datetime.combine(start_date, time.min)
                if start_time:
                    start_time = parse_time(start_time)
                    if start_time:
                        start_datetime = datetime.combine(start_date, start_time)
                logs = logs.filter(date_time__gte=timezone.make_aware(start_datetime))

        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                end_datetime = datetime.combine(end_date, time.max)
                if end_time:
                    end_time = parse_time(end_time)
                    if end_time:
                        end_datetime = datetime.combine(end_date, end_time)
                logs = logs.filter(date_time__lte=timezone.make_aware(end_datetime))

        paginator = Paginator(logs, 10)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context['logs'] = page_obj.object_list
        context['page_obj'] = page_obj
        context['action_choices'] = AuditLog.ACTION_CHOICES
        logger.debug(f"Audit logs retrieved: {list(page_obj.object_list.values('id', 'entity_name', 'object_id', 'action', 'created_by__username', 'date_time'))}")
        return context

def audit_log_table_body(request):
    if not request.session.get('user'):
        return HttpResponse('', status=403)
    
    query = request.GET.get('q', '')
    action_filter = request.GET.get('action', '')
    start_date = request.GET.get('start_date', '')
    start_time = request.GET.get('start_time', '')
    end_date = request.GET.get('end_date', '')
    end_time = request.GET.get('end_time', '')
    page_number = request.GET.get('page', 1)

    logs = AuditLog.objects.all().select_related('created_by', 'content_type').order_by('-date_time')
    
    if query:
        logs = logs.filter(
            Q(entity_name__icontains=query) |
            Q(object_id__icontains=query) |
            Q(created_by__username__icontains=query)
        )
    
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    if start_date:
        start_date = parse_date(start_date)
        if start_date:
            start_datetime = datetime.combine(start_date, time.min)
            if start_time:
                start_time = parse_time(start_time)
                if start_time:
                    start_datetime = datetime.combine(start_date, start_time)
            logs = logs.filter(date_time__gte=timezone.make_aware(start_datetime))
    
    if end_date:
        end_date = parse_date(end_date)
        if end_date:
            end_datetime = datetime.combine(end_date, time.max)
            if end_time:
                end_time = parse_time(end_time)
                if end_time:
                    end_datetime = datetime.combine(end_date, end_time)
            logs = logs.filter(date_time__lte=timezone.make_aware(end_datetime))
    
    paginator = Paginator(logs, 10)
    page_obj = paginator.get_page(page_number)

    logger.debug(f"Filtered audit logs: {list(page_obj.object_list.values('id', 'entity_name', 'object_id', 'action', 'created_by__username', 'date_time'))}")
    return render(request, 'audit_log_table_body.html', {'logs': page_obj.object_list, 'page_obj': page_obj})

def audit_log_export_pdf(request):
    if not request.session.get('user'):
        return HttpResponse('Non autorisé', status=403)
    
    query = request.GET.get('q', '')
    action_filter = request.GET.get('action', '')
    start_date = request.GET.get('start_date', '')
    start_time = request.GET.get('start_time', '')
    end_date = request.GET.get('end_date', '')
    end_time = request.GET.get('end_time', '')
    
    logs = AuditLog.objects.all().select_related('created_by', 'content_type').order_by('-date_time')
    
    if query:
        logs = logs.filter(
            Q(entity_name__icontains=query) |
            Q(object_id__icontains=query) |
            Q(created_by__username__icontains=query)
        )
    
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    if start_date:
        start_date = parse_date(start_date)
        if start_date:
            start_datetime = datetime.combine(start_date, time.min)
            if start_time:
                start_time = parse_time(start_time)
                if start_time:
                    start_datetime = datetime.combine(start_date, start_time)
            logs = logs.filter(date_time__gte=timezone.make_aware(start_datetime))
    
    if end_date:
        end_date = parse_date(end_date)
        if end_date:
            end_datetime = datetime.combine(end_date, time.max)
            if end_time:
                end_time = parse_time(end_time)
                if end_time:
                    end_datetime = datetime.combine(end_date, end_time)
            logs = logs.filter(date_time__lte=timezone.make_aware(end_datetime))
    
    action_label = dict(AuditLog.ACTION_CHOICES).get(action_filter, 'Toutes')
    
    start_datetime_str = f"{start_date} {start_time}" if start_date and start_time else start_date or 'Aucune'
    end_datetime_str = f"{end_date} {end_time}" if end_date and end_time else end_date or 'Aucune'
    
    context = {
        'logs': logs,
        'search_query': query,
        'action_label': action_label,
        'start_datetime': start_datetime_str,
        'end_datetime': end_datetime_str,
        'export_date': timezone.now(),
    }
    
    html_string = render_to_string('audit_log_pdf.html', context)
    
    try:
        html = HTML(string=html_string)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="journaux_audit.pdf"'
        html.write_pdf(response)
        logger.debug(f"PDF exporté pour les journaux d'audit avec query='{query}', action='{action_filter}', start_date='{start_date}', start_time='{start_time}', end_date='{end_date}', end_time='{end_time}'")
        
        AuditLog.objects.create(
            created_by=request.user,
            entity_name='AuditLogExport',
            object_id='PDF-EXPORT',
            content_type=ContentType.objects.get_for_model(AuditLog),
            action='impression',
            date_time=timezone.now()
        )
        
        return response
    except Exception as e:
        logger.error(f"Erreur lors de l'exportation PDF : {str(e)}", exc_info=True)
        return HttpResponse('Erreur lors de la génération du PDF', status=500)

def essential_components_view(request):
    """
    View for the essential components page with only the most used components
    """
    context = {
        'page_title': 'Composants Essentiels',
        'page_icon': 'cubes',
    }
    
    return render(request, 'essential_components.html', context)
# Ajouter ces vues à votre fichier views.py existant



@require_session_user
def user_management_dashboard(request):
    """
    Vue pour le dashboard de gestion des utilisateurs et logs
    """
    # Statistiques des utilisateurs
    total_users = User.objects.count()
    active_users = User.objects.filter(is_activated=True).count()
    inactive_users = User.objects.filter(is_activated=False).count()
    superusers = User.objects.filter(is_superuser=True).count()
    
    # Statistiques des logs (derniers 30 jours)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    total_logs = AuditLog.objects.filter(date_time__gte=thirty_days_ago).count()
    
    # Utilisateurs récents (derniers 10)
    recent_users = User.objects.select_related('employee').order_by('-pk')[:10]
    
    # Logs récents (derniers 10)
    recent_logs = AuditLog.objects.select_related('created_by', 'content_type').order_by('-date_time')[:10]
    
    # Actions les plus fréquentes
    top_actions = AuditLog.objects.filter(
        date_time__gte=thirty_days_ago
    ).values('action').annotate(
        count=Count('action')
    ).order_by('-count')[:5]
    
    # Utilisateurs les plus actifs
    active_users_stats = AuditLog.objects.filter(
        date_time__gte=thirty_days_ago
    ).values(
        'created_by__username', 'created_by__nom', 'created_by__prenom'
    ).annotate(
        count=Count('created_by')
    ).order_by('-count')[:5]
    
    context = {
        'page_title': 'Dashboard - Gestion des Utilisateurs',
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'superusers': superusers,
        'total_logs': total_logs,
        'recent_users': recent_users,
        'recent_logs': recent_logs,
        'top_actions': top_actions,
        'active_users_stats': active_users_stats,
        'action_choices': AuditLog.ACTION_CHOICES,
    }
    
    return render(request, 'user_management_dashboard.html', context)

@require_session_user_json
def users_evolution_api(request):
    """
    API pour l'évolution des créations d'utilisateurs (derniers 12 mois)
    """
    try:
        twelve_months_ago = timezone.now() - timedelta(days=365)
        
        # Grouper par mois
        users_by_month = User.objects.filter(
            pk__isnull=False
        ).extra(
            select={'month': "DATE_FORMAT(date_joined, '%%Y-%%m')"}
        ).values('month').annotate(
            count=Count('pk')
        ).order_by('month')
        
        # Formater les données pour Chart.js
        labels = []
        data = []
        
        for item in users_by_month[-12:]:  # Derniers 12 mois
            try:
                month_date = datetime.strptime(item['month'], '%Y-%m')
                labels.append(month_date.strftime('%b %Y'))
                data.append(item['count'])
            except:
                continue
                
        return JsonResponse({
            'labels': labels,
            'data': data
        })
    except Exception as e:
        logger.error(f"Error in users_evolution_api: {str(e)}", exc_info=True)
        return JsonResponse({'labels': [], 'data': []})

@require_session_user_json
def logs_by_action_api(request):
    """
    API pour la répartition des logs par action (derniers 30 jours)
    """
    try:
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        actions_data = AuditLog.objects.filter(
            date_time__gte=thirty_days_ago
        ).values('action').annotate(
            count=Count('action')
        ).order_by('-count')
        
        labels = []
        data = []
        
        action_labels = dict(AuditLog.ACTION_CHOICES)
        
        for item in actions_data:
            labels.append(action_labels.get(item['action'], item['action'].title()))
            data.append(item['count'])
            
        return JsonResponse({
            'labels': labels,
            'data': data
        })
    except Exception as e:
        logger.error(f"Error in logs_by_action_api: {str(e)}", exc_info=True)
        return JsonResponse({'labels': [], 'data': []})

@require_session_user_json
def users_activity_api(request):
    """
    API pour l'activité des utilisateurs (derniers 7 jours)
    """
    try:
        seven_days_ago = timezone.now() - timedelta(days=7)
        
        # Activité par jour
        daily_activity = AuditLog.objects.filter(
            date_time__gte=seven_days_ago
        ).extra(
            select={'day': "DATE_FORMAT(date_time, '%%Y-%%m-%%d')"}
        ).values('day').annotate(
            count=Count('pk')
        ).order_by('day')
        
        labels = []
        data = []
        
        for item in daily_activity:
            try:
                day_date = datetime.strptime(item['day'], '%Y-%m-%d')
                labels.append(day_date.strftime('%d/%m'))
                data.append(item['count'])
            except:
                continue
                
        return JsonResponse({
            'labels': labels,
            'data': data
        })
    except Exception as e:
        logger.error(f"Error in users_activity_api: {str(e)}", exc_info=True)
        return JsonResponse({'labels': [], 'data': []})

@require_session_user_json
def users_filtered_api(request):
    """
    API pour filtrer les utilisateurs
    """
    try:
        query = request.POST.get('q', '')
        status = request.POST.get('status', '')
        role = request.POST.get('role', '')
        
        users = User.objects.select_related('employee').order_by('-pk')
        
        if query:
            users = users.filter(
                Q(username__icontains=query) |
                Q(nom__icontains=query) |
                Q(prenom__icontains=query)
            )
        
        if status == 'active':
            users = users.filter(is_activated=True)
        elif status == 'inactive':
            users = users.filter(is_activated=False)
            
        if role == 'superuser':
            users = users.filter(is_superuser=True)
        elif role == 'staff':
            users = users.filter(is_staff=True, is_superuser=False)
        elif role == 'regular':
            users = users.filter(is_staff=False, is_superuser=False)
        
        users_list = []
        for user in users[:10]:  # Limiter à 10 résultats
            users_list.append({
                'id': user.pk,
                'username': user.username,
                'nom': user.nom,
                'prenom': user.prenom,
                'is_activated': user.is_activated,
                'is_superuser': user.is_superuser,
                'is_staff': user.is_staff,
                'employee_name': user.employee.full_name if user.employee else 'N/A',
                'date_joined': user.date_joined.strftime('%d/%m/%Y') if hasattr(user, 'date_joined') else 'N/A'
            })
        
        return JsonResponse({'users': users_list})
        
    except Exception as e:
        logger.error(f"Error in users_filtered_api: {str(e)}", exc_info=True)
        return JsonResponse({'users': []})

@require_session_user_json
def logs_filtered_api(request):
    """
    API pour filtrer les logs
    """
    try:
        query = request.POST.get('q', '')
        action = request.POST.get('action', '')
        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')
        
        logs = AuditLog.objects.select_related('created_by', 'content_type').order_by('-date_time')
        
        if query:
            logs = logs.filter(
                Q(entity_name__icontains=query) |
                Q(object_id__icontains=query) |
                Q(created_by__username__icontains=query)
            )
        
        if action:
            logs = logs.filter(action=action)
            
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                logs = logs.filter(date_time__gte=timezone.make_aware(start_date_obj))
            except:
                pass
                
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59)
                logs = logs.filter(date_time__lte=timezone.make_aware(end_date_obj))
            except:
                pass
        
        logs_list = []
        action_labels = dict(AuditLog.ACTION_CHOICES)
        
        for log in logs[:10]:  # Limiter à 10 résultats
            logs_list.append({
                'id': log.pk,
                'entity_name': log.entity_name,
                'object_id': log.object_id,
                'action': log.action,
                'action_display': action_labels.get(log.action, log.action.title()),
                'created_by': log.created_by.username if log.created_by else 'Système',
                'date_time': log.date_time.strftime('%d/%m/%Y %H:%M'),
                'content_type': str(log.content_type) if log.content_type else 'N/A'
            })
        
        return JsonResponse({'logs': logs_list})
        
    except Exception as e:
        logger.error(f"Error in logs_filtered_api: {str(e)}", exc_info=True)
        return JsonResponse({'logs': []})