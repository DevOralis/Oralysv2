from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction

from apps.hr.models.medical_visit import MedicalVisit
from django.utils.dateparse import parse_date
from .models.department import Department
from .models.position import Position
from .models.contract_type import ContractType
from .models.contract import Contract
from .models.employee import Employee
from .models.child import Child
from .models.leave_type import LeaveType
from .models.leave_balance import LeaveBalance
from .models.leave_request import LeaveRequest
from .models.leave_approval import LeaveApproval
from apps.patient.models.acte import Acte
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib import messages
import json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from datetime import datetime, timedelta
from decimal import Decimal
import os
from django.conf import settings
from .models.social_contribution import SocialContribution
from .models.prime import Prime
from .models.model_calcul import ModelCalcul, get_total_primes_et_cotisations
from django.template.loader import get_template, render_to_string
from xhtml2pdf import pisa
from django.views.decorators.csrf import csrf_exempt
try:
    from weasyprint import HTML
except Exception:
    HTML = None
from math import ceil
from calendar import month_name, monthrange
import locale
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
from .models.payroll_history import PayrollGenerationHistory
from .models.speciality import Speciality
from apps.home.utils import log_action

def initialize_leave_balances(employee_id, year):
    """
    Initialise ou récupère les soldes de congés pour un employé et une année donnée
    """
    # Filtrer pour n'inclure que les types de congés actifs avec default_days > 0
    leave_types = LeaveType.objects.filter(active=True, default_days__gt=0)
    balances = []
    
    for leave_type in leave_types:
        # Utiliser une valeur par défaut si default_days est None (ne devrait plus arriver avec le filtre)
        default_days = leave_type.default_days or Decimal('0')
        
        balance, created = LeaveBalance.objects.get_or_create(
            employee_id=employee_id,
            leave_type=leave_type,
            year=year,
            defaults={
                'entitlement': default_days,
                'taken': 0,
                'remaining': default_days
            }
        )
        balances.append(balance)
    
    return balances


def hr(request):
    # Rediriger les utilisateurs hors RH vers la gestion des congés
    sess_user = request.session.get('user')
    if sess_user:
        if not sess_user.get('is_hr_employee', False):
            return redirect('gestion_conges')
    # Paramètre pour éditer un employé spécifique
    employee_id = request.GET.get('employee_id')
    employee = None
    children = []
    skills = []
    children_json = '[]'
    if employee_id:
        # Charger l'employé avec ses relations
        employee = Employee.objects.filter(id=employee_id).select_related(
            'position', 
            'department'
        ).prefetch_related('children', 'contracts__contract_type').first()
        if employee:
            # Récupérer les enfants
            children = list(employee.children.all())
            # Convertir les enfants en format JSON pour JavaScript
            children_json = json.dumps([
                {
                    'name': child.name, 
                    'gender': child.gender,
                    'birth_date': child.birth_date.strftime('%Y-%m-%d') if child.birth_date else '',
                    'date_naissance': child.birth_date.strftime('%Y-%m-%d') if child.birth_date else '',
                    'is_scolarise': child.is_scolarise
                } for child in children
            ])
            # Récupération des compétences
            if employee.skills:
                skills = [skill for skill in employee.skills.split(',') if skill.strip()]
            # Conversion des valeurs numériques en chaînes de caractères
            base_salary_str = str(employee.base_salary) if employee.base_salary is not None else '0'
            # Récupération des visites médicales
            from .models.medical_visit import MedicalVisit
            medical_visits = list(MedicalVisit.objects.filter(employee=employee))
            medical_visits = list(MedicalVisit.objects.filter(employee=employee))
            medical_visits_data = [
                {
                    'id': visit.id,
                    'doctor_name': visit.doctor_name,
                    'visit_date': visit.visit_date.strftime('%Y-%m-%d') if visit.visit_date else '',
                    'result_file': visit.result_file.url if visit.result_file else ''
                } for visit in medical_visits
            ]
            medical_visits_json = json.dumps(medical_visits_data)
            print(f"Medical visits data: {medical_visits_data}")  # Debug
            print(f"Medical visits JSON: {medical_visits_json}")  # Debug
    # Récupérer la liste des médecins
    medecins = Employee.objects.filter(position__name__icontains='médecin')
    # Convertir les médecins en format JSON pour JavaScript
    medecins_data = [
        {
            'id': medecin.id,
            'full_name': medecin.full_name,
            'position_name': medecin.position.name if medecin.position else ''
        } for medecin in medecins
    ]
    medecins_json = json.dumps(medecins_data)
    print(f"Medecins data: {medecins_data}")  # Debug
    print(f"Medecins JSON: {medecins_json}")  # Debug

    context = {
        'page_title': 'Human Resources',
        'positions': Position.objects.all(),
        'departments': Department.objects.all(),
        'contract_types': ContractType.objects.all(),
        'employees': Employee.objects.select_related('position', 'department').prefetch_related('children', 'contracts__contract_type'),
        'medecins': medecins,  # Ajouter les médecins au contexte
        'medecins_json': medecins_json,  # Ajouter les médecins en format JSON
        'supervisors': Employee.objects.filter(is_supervisor=1).select_related('department'),
        'department_supervisors': Employee.objects.filter(is_supervisor=1).select_related('department').values('department__name', 'full_name', 'department_id').distinct(),
        'employee': employee,
        'children': children,
        'children_json': children_json,
        'skills': skills,
        'base_salary_str': base_salary_str if 'base_salary_str' in locals() else '0',
        'model_calculs': ModelCalcul.objects.all(),
        'specialities': Speciality.objects.all(),
        'medical_visits_json': medical_visits_json if 'medical_visits_json' in locals() else '[]',
    }
    return render(request, 'hr.html', context)

def hr_statistics(request):
    """
    Vue pour le dashboard HR avec statistiques
    """
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    # Statistiques principales
    total_employees = Employee.objects.filter(status='A').count()
    pending_leaves = LeaveRequest.objects.filter(status='submitted').count()
    total_departments = Department.objects.count()
    
    # Bulletins de paie ce mois-ci
    current_month = timezone.now().replace(day=1)
    total_payrolls = PayrollGenerationHistory.objects.count()
    
    # Total des congés accordés
    total_leave_requests = LeaveRequest.objects.count()
    
    # Statistiques par département
    department_stats = Department.objects.annotate(
        employee_count=Count('employee', filter=Q(employee__status='A'))
    ).filter(employee_count__gt=0)
    
    # Demandes de congés en attente
    pending_leave_requests = LeaveRequest.objects.filter(
        status='submitted'
    ).select_related('employee', 'leave_type')[:5]
    
    # Nouveaux employés (les 5 derniers)
    new_employees = Employee.objects.filter(
        status='A'
    ).select_related('department', 'position').order_by('-id')[:5]
    
    # Statistiques par statut marital
    marital_stats = Employee.objects.filter(status='A').values('marital_status').annotate(
        count=Count('id')
    )
    
    # Statistiques par genre
    gender_stats = Employee.objects.filter(status='A').values('gender').annotate(
        count=Count('id')
    )
    
    # Statistiques par salaire (tranches)
    salary_ranges = [
        {'range': '< 5000 DH', 'min': 0, 'max': 5000},
        {'range': '5000-10000 DH', 'min': 5000, 'max': 10000},
        {'range': '10000-15000 DH', 'min': 10000, 'max': 15000},
        {'range': '> 15000 DH', 'min': 15000, 'max': 999999}
    ]
    
    salary_stats = []
    for salary_range in salary_ranges:
        count = Employee.objects.filter(
            status='A',
            base_salary__gte=salary_range['min'],
            base_salary__lt=salary_range['max']
        ).count()
        salary_stats.append({
            'range': salary_range['range'],
            'count': count
        })
    
    # Employés avec enfants vs sans enfants
    employees_with_children = Employee.objects.filter(status='A', children_count__gt=0).count()
    employees_without_children = Employee.objects.filter(status='A', children_count=0).count()
    
    # Évolution des congés par mois (6 derniers mois)
    leaves_by_month = []
    for i in range(6):
        month_start = (timezone.now().replace(day=1) - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        count = LeaveRequest.objects.filter(
            start_date__gte=month_start,
            start_date__lte=month_end
        ).count()
        
        leaves_by_month.append({
            'month_name': month_start.strftime('%B'),
            'count': count
        })
    
    leaves_by_month.reverse()  # Ordre chronologique
    
    # Préparer les données JSON pour les graphiques
    import json
    department_stats_json = json.dumps([
        {'name': dept.name, 'employee_count': dept.employee_count} 
        for dept in department_stats
    ])
    
    leaves_by_month_json = json.dumps([
        {'month_name': month['month_name'], 'count': month['count']} 
        for month in leaves_by_month
    ])
    
    # Données JSON pour les nouveaux graphiques
    marital_stats_json = json.dumps([
        {'status': dict(Employee.MARITAL_STATUS_CHOICES).get(item['marital_status'], item['marital_status']), 'count': item['count']} 
        for item in marital_stats
    ])
    
    gender_stats_json = json.dumps([
        {'gender': 'Hommes' if item['gender'] == 'M' else 'Femmes', 'count': item['count']} 
        for item in gender_stats
    ])
    
    salary_stats_json = json.dumps(salary_stats)
    
    children_stats_json = json.dumps([
        {'category': 'Avec enfants', 'count': employees_with_children},
        {'category': 'Sans enfants', 'count': employees_without_children}
    ])
    
    context = {
        'total_employees': total_employees,
        'total_leave_requests': total_leave_requests,
        'total_departments': total_departments,
        'total_payrolls': total_payrolls,
        'department_stats': department_stats,
        'pending_leave_requests': pending_leave_requests,
        'new_employees': new_employees,
        'marital_stats': marital_stats,
        'gender_stats': gender_stats,
        'salary_stats': salary_stats,
        'employees_with_children': employees_with_children,
        'employees_without_children': employees_without_children,
        'leaves_by_month': leaves_by_month,
        'department_stats_json': department_stats_json,
        'leaves_by_month_json': leaves_by_month_json,
        'marital_stats_json': marital_stats_json,
        'gender_stats_json': gender_stats_json,
        'salary_stats_json': salary_stats_json,
        'children_stats_json': children_stats_json,
    }
    
    return render(request, 'hr_statistics.html', context)

def get_employe_data(request, employe_id):
    try:
        employee = Employee.objects.select_related(
            'position', 
            'department', 
            'supervisor'
        ).prefetch_related('children', 'contracts__contract_type').get(id=employe_id)
        
        # Récupération des enfants
        children = []
        for child in employee.children.all():
            children.append({
                'name': child.name,
                'gender': child.gender
            })
        
        # Préparation des données du contrat
        contract_data = None
        if hasattr(employee, 'contract') and employee.contract:
            contract = employee.contract
            contract_data = {
                'contract_type_id': contract.contract_type.id,
                'contract_type_name': contract.contract_type.name,
                'start_date': contract.start_date.strftime('%Y-%m-%d') if contract.start_date else None,
                'end_date': contract.end_date.strftime('%Y-%m-%d') if contract.end_date else None
            }
        
        # Préparation des données de l'employé
        employee_data = {
            'id': employee.id,
            'first_name': employee.first_name,
            'last_name': employee.last_name,
            'gender': employee.gender,
            'birth_date': employee.birth_date.strftime('%Y-%m-%d') if employee.birth_date else None,
            'national_id': employee.national_id,
            'address': employee.address,
            'phone': employee.phone,
            'email': employee.email,
            'hire_date': employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else None,
            'position_id': employee.position.id if employee.position else None,
            'department_id': employee.department.id if employee.department else None,
            'supervisor_id': employee.supervisor.id if employee.supervisor else None,
            'base_salary': float(employee.base_salary) if employee.base_salary is not None else 0,
            # 'bonuses': float(employee.bonuses) if employee.bonuses is not None else 0,
            # 'benefits': float(employee.benefits) if employee.benefits is not None else 0,
            'skills': employee.skills or '',
            'children': children,
            'contract': contract_data
        }
        
        return JsonResponse({'status': 'success', 'employee': employee_data})
        
    except Employee.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Employé non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
def _save_medical_visits(request, employee):
    """
    Crée / met à jour / supprime les visites médicales sans jamais fixer manuellement l'ID.
    - Updates uniquement si medical_visit_id_<i> est fourni ET appartient à l'employé
    - Creates si pas d'ID
    - Deletes via flags medical_visit_delete_<ID>=true (posés par le front)
    """
    # 0) Suppressions demandées par le formulaire
    delete_ids = []
    for key, val in request.POST.items():
        if key.startswith('medical_visit_delete_') and val == 'true':
            try:
                delete_ids.append(int(key.split('medical_visit_delete_')[1]))
            except ValueError:
                pass
    if delete_ids:
        MedicalVisit.objects.filter(employee=employee, id__in=delete_ids).delete()

    # 1) Nombre de lignes annoncées par le form
    try:
        count = int(request.POST.get('medical_visits_count', 0))
    except (TypeError, ValueError):
        count = 0

    # 2) Parcours des lignes (0..count-1)
    for i in range(count):
        visit_id = (request.POST.get(f'medical_visit_id_{i}') or '').strip()
        doctor   = (request.POST.get(f'medical_visit_doctor_{i}') or '').strip()
        date_str = (request.POST.get(f'medical_visit_date_{i}') or '').strip()
        file_obj = request.FILES.get(f'medical_visit_result_{i}')

        # Sauter les lignes complètement vides
        if not doctor and not date_str and not file_obj and not visit_id:
            continue

        # Parse date (None si vide/mauvais format)
        visit_date = parse_date(date_str) if date_str else None

        if visit_id.isdigit():
            # UPDATE sécurisé : uniquement si la visite appartient à l'employé
            mv = MedicalVisit.objects.filter(id=int(visit_id), employee=employee).first()
            if not mv:
                # ID inconnu / supprimé : on ignore pour éviter tout risque de collision
                continue
            mv.doctor_name = doctor
            mv.visit_date  = visit_date
            if file_obj:
                mv.result_file = file_obj
            mv.save()
        else:
            # CREATE : surtout ne jamais mettre mv.id = ...
            mv = MedicalVisit(
                employee=employee,
                doctor_name=doctor,
                visit_date=visit_date,
            )
            if file_obj:
                mv.result_file = file_obj
            mv.save()

@transaction.atomic
def add_employee(request):
    
    if request.method == 'POST':
        try:
            # Récupération des données du formulaire
            full_name = request.POST.get('full_name')
            gender = request.POST.get('gender')
            birth_date = request.POST.get('date_of_birth')
            national_id = request.POST.get('national_id') or request.POST.get('cin')
            if not national_id or not national_id.strip():
                messages.error(request, "Le champ CIN (national_id) est obligatoire.")
                return redirect('human_resources')
            personal_address = request.POST.get('personal_address')
            work_address = request.POST.get('work_address')
            personal_phone = request.POST.get('personal_phone')
            work_phone = request.POST.get('work_phone')
            email = request.POST.get('email')
            marital_status = request.POST.get('marital_status')
            status = request.POST.get('status', 'A')
            position_id = request.POST.get('position')
            department_id = request.POST.get('department')
            is_supervisor = request.POST.get('is_supervisor', '0')
            supervisor_id = request.POST.get('responsible_select')
            
            # Traitement des valeurs monétaires
            base_salary = request.POST.get('base_salary', '0')
            # bonuses = request.POST.get('bonuses', '0')
            # benefits = request.POST.get('benefits', '0')
            
            # Conversion en valeurs numériques
            base_salary = float(base_salary.replace(',', '.')) if base_salary else 0
            # bonuses = float(bonuses.replace(',', '.')) if bonuses else 0
            # benefits = float(benefits.replace(',', '.')) if benefits else 0
            
            # Récupération des compétences
            skills = []
            # Récupérer les compétences des champs skills_0, skills_1, etc.
            for key in request.POST:
                if key.startswith('skills_') and request.POST[key].strip():
                    skills.append(request.POST[key].strip())
            # Si aucun champ skills_ trouvé, vérifier le champ skills (pour rétrocompatibilité)
            if not skills and 'skills' in request.POST and request.POST['skills'].strip():
                skills = [s.strip() for s in request.POST['skills'].split(',') if s.strip()]
            # Créer une chaîne séparée par des virgules
            skills_str = ','.join(skills)
            
            # Récupération des données de carrière
            career_evolution = request.POST.get('career_evolution', '')
            
            # Création ou mise à jour de l'employé
            employee_id_value = request.POST.get('employee_id')
            db_employee_id = request.POST.get('db_employee_id')
            
            # Nouveau : récupération du modèle de calcul
            model_calcul_id = request.POST.get('model_calcul')
            # Ajout : récupération de la spécialité
            speciality_id = request.POST.get('speciality')
            
            if db_employee_id:
                # Mise à jour d'un employé existant
                employee = Employee.objects.get(id=db_employee_id)
                employee.employee_id = employee_id_value
                employee.full_name = full_name
                employee.gender = gender
                employee.birth_date = birth_date
                employee.national_id = national_id
                employee.personal_address = personal_address
                employee.work_address = work_address
                employee.personal_phone = personal_phone
                employee.work_phone = work_phone
                employee.email = email
                employee.marital_status = marital_status
                employee.status = status
                employee.position_id = position_id
                employee.department_id = department_id
                employee.is_supervisor = is_supervisor
                employee.supervisor_id = supervisor_id if supervisor_id else None
                employee.base_salary = base_salary
                # employee.bonuses = bonuses
                # employee.benefits = benefits
                employee.skills = skills_str
                employee.career_evolution = career_evolution
                # Ajout : mise à jour du modèle de calcul
                employee.model_calcul_id = model_calcul_id if model_calcul_id else None
                # Ajout : mise à jour de la spécialité
                employee.speciality_id = speciality_id if speciality_id else None
                
                # Gestion des fichiers uploadés
                if 'photo' in request.FILES:
                    employee.photo = request.FILES['photo']
                if 'legalized_contract' in request.FILES:
                    employee.legalized_contract = request.FILES['legalized_contract']
                if 'doctor_agreement' in request.FILES:
                    employee.doctor_agreement = request.FILES['doctor_agreement']
                if 'temporary_agreement' in request.FILES:
                    employee.temporary_agreement = request.FILES['temporary_agreement']
                
                employee.save()
                _save_medical_visits(request, employee)
                log_action(request.user, employee, 'modification')
                
                # Traitement des visites médicales
                from .models.medical_visit import MedicalVisit
                import os
                from django.conf import settings
                
                # Récupérer le nombre de visites médicales
                medical_visits_count = int(request.POST.get('medical_visits_count', '0'))
                print(f"=== TRAITEMENT DES VISITES MÉDICALES ===")
                print(f"Nombre de visites médicales à traiter: {medical_visits_count}")
                
                # Gérer la suppression des visites médicales existantes
                # Rechercher les champs de suppression
                delete_keys = [key for key in request.POST.keys() if key.startswith('medical_visit_delete_')]
                print(f"Clés de suppression trouvées: {delete_keys}")
                
                for delete_key in delete_keys:
                    # Extraire l'ID de la visite à supprimer
                    try:
                        visit_id = int(delete_key.split('_')[-1])
                        print(f"Tentative de suppression de la visite médicale ID: {visit_id}")
                        
                        # Trouver la visite médicale existante
                        try:
                            medical_visit = MedicalVisit.objects.get(id=visit_id, employee=employee)
                            medical_visit.delete()
                            print(f"Visite médicale ID {visit_id} supprimée avec succès")
                        except MedicalVisit.DoesNotExist:
                            print(f"Visite médicale ID {visit_id} non trouvée pour cet employé")
                    except (ValueError, IndexError):
                        print(f"Erreur d'extraction de l'ID de suppression depuis la clé: {delete_key}")
                
                # Créer ou mettre à jour les visites médicales
                for i in range(medical_visits_count):
                    doctor_name_key = f'medical_visit_doctor_{i}'
                    visit_date_key = f'medical_visit_date_{i}'
                    result_file_key = f'medical_visit_result_{i}'
                    
                    print(f"--- Visite médicale {i} ---")
                    print(f"Clés recherchées: {doctor_name_key}, {visit_date_key}, {result_file_key}")
                    print(f"Toutes les clés POST: {list(request.POST.keys())}")
                    print(f"Tous les fichiers POST: {list(request.FILES.keys())}")
                    
                    if doctor_name_key in request.POST and visit_date_key in request.POST:
                        doctor_name = request.POST.get(doctor_name_key)
                        visit_date_str = request.POST.get(visit_date_key)
                        result_file = request.FILES.get(result_file_key)
                        
                        print(f"Données reçues - Médecin: {doctor_name}, Date: {visit_date_str}")
                        
                        # Conversion de la date de visite
                        visit_date = None
                        if visit_date_str and visit_date_str.strip():
                            try:
                                from datetime import datetime as dt
                                visit_date = dt.strptime(visit_date_str, '%Y-%m-%d').date()
                                print(f"Date convertie: {visit_date}")
                            except ValueError as e:
                                print(f"Erreur de conversion de date: {e}")
                                visit_date = None
                        
                        # Création de la visite médicale
                        if doctor_name and visit_date:
                            medical_visit = MedicalVisit.objects.create(
                                employee=employee,
                                doctor_name=doctor_name,
                                visit_date=visit_date
                            )
                            log_action(request.user, medical_visit, 'creation')
                            
                            # Gestion du fichier de résultat
                            if result_file:
                                medical_visit.result_file = result_file
                                medical_visit.save()
                            
                            print(f"Visite médicale créée: {medical_visit.doctor_name}, Date: {medical_visit.visit_date}")
                        else:
                            print(f"Visite médicale non créée - Données manquantes: Médecin={doctor_name}, Date={visit_date}")
                    else:
                        print(f"Visite médicale non créée - Clés manquantes: doctor_name_key={doctor_name_key in request.POST}, visit_date_key={visit_date_key in request.POST}")
                
                # Supprimer les enfants existants pour les remplacer par les nouveaux
                # On supprime physiquement les objets Child pour éviter les orphelins
                for child in employee.children.all():
                    child.delete()
                employee.children.clear()
                
            else:
                # Création d'un nouvel employé
                employee = Employee(
                    employee_id=employee_id_value,
                    full_name=full_name,
                    gender=gender,
                    birth_date=birth_date,
                    national_id=national_id,
                    personal_address=personal_address,
                    work_address=work_address,
                    personal_phone=personal_phone,
                    work_phone=work_phone,
                    email=email,
                    marital_status=marital_status,
                    status=status,
                    position_id=position_id,
                    department_id=department_id,
                    is_supervisor=is_supervisor,
                    supervisor_id=supervisor_id if supervisor_id else None,
                    base_salary=base_salary,
                    skills=skills_str,
                    career_evolution=career_evolution,
                    children_count=int(request.POST.get('children_count', '0')),
                    model_calcul_id=model_calcul_id if model_calcul_id else None,
                    # Ajout : spécialité
                    speciality_id=speciality_id if speciality_id else None
                )
                
                # Gestion des fichiers uploadés
                if 'photo' in request.FILES:
                    employee.photo = request.FILES['photo']
                if 'legalized_contract' in request.FILES:
                    employee.legalized_contract = request.FILES['legalized_contract']
                if 'doctor_agreement' in request.FILES:
                    employee.doctor_agreement = request.FILES['doctor_agreement']
                if 'temporary_agreement' in request.FILES:
                    employee.temporary_agreement = request.FILES['temporary_agreement']
                
                employee.save()
                log_action(request.user, employee, 'creation')
            
            # Traitement des enfants - MODIFICATION ET CRÉATION
            from datetime import datetime
            children_count = int(request.POST.get('children_count', '0'))
            print(f"=== TRAITEMENT DES ENFANTS ===")
            print(f"Nombre d'enfants à traiter: {children_count}")
            print(f"Type d'opération: {'MODIFICATION' if db_employee_id else 'CRÉATION'}")
            print(f"Toutes les clés POST: {list(request.POST.keys())}")  # Debug
            
            for i in range(children_count):
                name_key = f'enfant_nom_{i}'
                gender_key = f'enfant_genre_{i}'
                birth_date_key = f'enfant_date_naissance_{i}'
                is_scolarise_key = f'enfant_is_scolarise_{i}'
                
                print(f"--- Enfant {i} ---")
                print(f"Clés recherchées: {name_key}, {gender_key}, {birth_date_key}, {is_scolarise_key}")
                print(f"Présence dans POST: nom={name_key in request.POST}, genre={gender_key in request.POST}, date={birth_date_key in request.POST}, scolarise={is_scolarise_key in request.POST}")
                
                if name_key in request.POST and gender_key in request.POST:
                    child_name = request.POST.get(name_key)
                    child_gender = request.POST.get(gender_key)
                    child_birth_date_str = request.POST.get(birth_date_key)
                    child_is_scolarise_str = request.POST.get(is_scolarise_key)
                    
                    print(f"Données reçues - Nom: {child_name}, Genre: {child_gender}, Date: {child_birth_date_str}, Scolarisé: {child_is_scolarise_str}")  # Debug

                    # Conversion de la date de naissance
                    child_birth_date = None
                    if child_birth_date_str and child_birth_date_str.strip():
                        try:
                            child_birth_date = datetime.strptime(child_birth_date_str, '%Y-%m-%d').date()
                            print(f"Date convertie: {child_birth_date}")  # Debug
                        except ValueError as e:
                            print(f"Erreur de conversion de date: {e}")  # Debug
                            child_birth_date = None
                    
                    # Conversion du statut scolarisé
                    child_is_scolarise = child_is_scolarise_str == "1" if child_is_scolarise_str else False
                    print(f"Statut scolarisé converti: {child_is_scolarise}")  # Debug

                    child = Child.objects.create(
                        name=child_name,
                        gender=child_gender,
                        birth_date=child_birth_date,
                        is_scolarise=child_is_scolarise
                    )
                    log_action(request.user, child, 'creation')
                    employee.children.add(child)
                    print(f"Enfant créé: {child.name}, Date: {child.birth_date}, Scolarisé: {child.is_scolarise}")  # Debug
            
            # Traitement des visites médicales
            from .models.medical_visit import MedicalVisit
            import os
            from django.conf import settings
            
            # Gérer la suppression des visites médicales existantes
            delete_keys = [key for key in request.POST.keys() if key.startswith('medical_visit_delete_')]
            for delete_key in delete_keys:
                visit_id = int(delete_key.split('_')[-1])
                try:
                    medical_visit = MedicalVisit.objects.get(id=visit_id, employee=employee)
                    medical_visit.delete()
                    print(f"Visite médicale supprimée: ID {visit_id}")
                except MedicalVisit.DoesNotExist:
                    print(f"Visite médicale non trouvée pour suppression: ID {visit_id}")
                except Exception as e:
                    print(f"Erreur lors de la suppression de la visite médicale ID {visit_id}: {e}")
            
            # Récupérer le nombre de visites médicales
            medical_visits_count = int(request.POST.get('medical_visits_count', '0'))
            print(f"=== TRAITEMENT DES VISITES MÉDICALES ===")
            print(f"Nombre de visites médicales à traiter: {medical_visits_count}")
            
            # Récupérer les visites médicales existantes pour cet employé
            existing_medical_visits = list(MedicalVisit.objects.filter(employee=employee))
            print(f"Visites médicales existantes: {len(existing_medical_visits)}")
            
            # Créer un dictionnaire pour suivre les visites déjà traitées
            processed_visits = set()
            # Créer ou mettre à jour les visites médicales
            for i in range(medical_visits_count):
                doctor_name_key = f'medical_visit_doctor_{i}'
                visit_date_key = f'medical_visit_date_{i}'
                result_file_key = f'medical_visit_result_{i}'

                visit_id_key = f'medical_visit_id_{i}'  # ✅ ID transmis depuis le formulaire
                visit_id = request.POST.get(visit_id_key)

                print(f"--- Visite médicale {i} ---")

                if doctor_name_key in request.POST and visit_date_key in request.POST:
                    doctor_name = request.POST.get(doctor_name_key)
                    visit_date_str = request.POST.get(visit_date_key)
                    result_file = request.FILES.get(result_file_key)

                    try:
                        visit_date = datetime.strptime(visit_date_str, "%Y-%m-%d").date()
                    except Exception:
                        visit_date = None

                    # ✅ Recherche de la visite existante uniquement si un ID est fourni
                    if visit_id and visit_id.isdigit():
                        try:
                            medical_visit = MedicalVisit.objects.get(id=int(visit_id), employee=employee)
                        except MedicalVisit.DoesNotExist:
                            medical_visit = None
                    else:
                        medical_visit = None

                    # ✅ Si non trouvée → création (sans jamais fixer d'ID manuellement)
                    if medical_visit is None:
                        medical_visit = MedicalVisit.objects.create(
                            employee=employee,
                            doctor_name=doctor_name,
                            visit_date=visit_date
                        )
                    else:
                        medical_visit.doctor_name = doctor_name
                        medical_visit.visit_date = visit_date

                    if result_file:
                        medical_visit.result_file = result_file

                    medical_visit.save()


                        
            for i in range(medical_visits_count):
                doctor_name_key = f'medical_visit_doctor_{i}'
                visit_date_key = f'medical_visit_date_{i}'
                result_file_key = f'medical_visit_result_{i}'
                visit_id_key = f'medical_visit_id_{i}'  # Nouvelle clé pour l'ID de la visite
                
                print(f"--- Visite médicale {i} ---")
                print(f"Clés recherchées: {doctor_name_key}, {visit_date_key}, {result_file_key}, {visit_id_key}")
                print(f"Toutes les clés POST: {list(request.POST.keys())}")
                print(f"Tous les fichiers POST: {list(request.FILES.keys())}")
                
                if doctor_name_key in request.POST and visit_date_key in request.POST:
                    doctor_name = request.POST.get(doctor_name_key)
                    visit_date_str = request.POST.get(visit_date_key)
                    result_file = request.FILES.get(result_file_key)
                    visit_id = request.POST.get(visit_id_key)  # Récupérer l'ID de la visite
                    
                    print(f"Données reçues - Médecin: {doctor_name}, Date: {visit_date_str}, ID: {visit_id}")
                    
                    # Conversion de la date de visite
                    visit_date = None
                    if visit_date_str and visit_date_str.strip():
                        try:
                            from datetime import datetime as dt
                            visit_date = dt.strptime(visit_date_str, '%Y-%m-%d').date()
                            print(f"Date convertie: {visit_date}")
                        except ValueError as e:
                            print(f"Erreur de conversion de date: {e}")
                            visit_date = None
                    
                    # Création ou mise à jour de la visite médicale
                    if doctor_name and visit_date:
                        medical_visit = None
                        
                        # Si on a un ID de visite, essayer de trouver la visite existante
                        if visit_id and visit_id.isdigit():
                            try:
                                medical_visit = MedicalVisit.objects.get(id=int(visit_id), employee=employee)
                                print(f"Mise à jour de la visite médicale existante: ID {visit_id}")
                            except MedicalVisit.DoesNotExist:
                                print(f"Visite médicale non trouvée avec ID {visit_id}, création d'une nouvelle visite")
                        
                        # Si on n'a pas trouvé de visite existante, créer une nouvelle
                        if medical_visit is None:
                            medical_visit = MedicalVisit.objects.create(
                                employee=employee,
                                doctor_name=doctor_name,
                                visit_date=visit_date
                            )
                            log_action(request.user, medical_visit, 'creation')
                            
                            print(f"Visite médicale créée: {medical_visit.doctor_name}, Date: {medical_visit.visit_date}")
                        else:
                            # Mise à jour de la visite existante
                            medical_visit.doctor_name = doctor_name
                            medical_visit.visit_date = visit_date
                            print(f"Mise à jour de la visite médicale: {medical_visit.doctor_name}, Date: {medical_visit.visit_date}")
                        
                        # Marquer cette visite comme traitée
                        processed_visits.add(medical_visit.id)
                        
                        # Gestion du fichier de résultat
                        if result_file:
                            medical_visit.result_file = result_file
                        medical_visit.save()
                        
                    else:
                        print(f"Visite médicale non traitée - Données manquantes: Médecin={doctor_name}, Date={visit_date}")
                else:
                    print(f"Visite médicale non traitée - Clés manquantes: doctor_name_key={doctor_name_key in request.POST}, visit_date_key={visit_date_key in request.POST}")
            
            # Supprimer les visites qui n'ont pas été traitées (supprimées dans l'interface)
            for visit in existing_medical_visits:
                if visit.id not in processed_visits:
                    print(f"Suppression de la visite médicale non traitée: ID {visit.id}")
                    visit.delete()
            
            # Création du contrat
            contract_type_id = request.POST.get('contract_type')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            
            # Validation stricte des données de contrat
            if contract_type_id and start_date and start_date.strip():
                try:
                    # Récupérer le contrat existant ou en créer un nouveau
                    existing_contract = employee.contracts.first()
                    if existing_contract:
                        # Mettre à jour le contrat existant
                        existing_contract.contract_type_id = contract_type_id
                        existing_contract.start_date = start_date
                        existing_contract.end_date = end_date if end_date and end_date.strip() else None
                        existing_contract.save()
                        log_action(request.user, existing_contract, 'modification')
                    else:
                        # Créer un nouveau contrat
                        contract = Contract.objects.create(
                            employee=employee,
                            contract_type_id=contract_type_id,
                            start_date=start_date,
                            end_date=end_date if end_date and end_date.strip() else None
                        )
                        log_action(request.user, contract, 'creation')
                except Exception as e:
                    print(f"Erreur lors de la création/mise à jour du contrat: {e}")
                    print(f"Données reçues - contract_type_id: {contract_type_id}, start_date: '{start_date}', end_date: '{end_date}'")
            
            # Vérifier si c'est une requête AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            
            # Ajouter un message de succès
            messages.success(request, "Employé modifié avec succès.")
            
            # Rediriger vers la page des ressources humaines avec succès
            # Utiliser success=update pour les mises à jour au lieu de success=add
            return redirect(f'/hr/?success=update&edit_employee={employee.id}#employee-form')
            
        except Exception as e:
            print(f"Erreur lors de l'ajout/modification de l'employé: {str(e)}")
            
            # Vérifier si c'est une requête AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
            # Ajouter un message d'erreur
            messages.error(request, f"Erreur: {str(e)}")
            
            # Rediriger vers la page des ressources humaines
            return redirect('human_resources')
    
    # Si ce n'est pas une requête POST, rediriger vers la liste des employés
    return redirect('liste_employes')


@require_POST
@transaction.atomic
def supprimer_employe(request):
    employee_id = request.POST.get('employee_id')
    try:
        employee = Employee.objects.get(id=employee_id)
        log_action(request.user, employee, 'suppression')
        employee.delete()
        return JsonResponse({'status': 'success', 'message': 'Employé supprimé avec succès'})
    except Employee.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Employé introuvable'}, status=404)


def liste_employes(request):
    # Récupérer les filtres
    filter_name = request.GET.get('filter_name', '')
    filter_position = request.GET.get('filter_position', '')
    filter_department = request.GET.get('filter_department', '')
    
    # Récupérer les employés avec filtres
    employees = Employee.objects.select_related('position', 'department', 'contract__contract_type')
    
    if filter_name:
        employees = employees.filter(
            Q(first_name__icontains=filter_name) | 
            Q(last_name__icontains=filter_name)
        )
    
    if filter_position:
        employees = employees.filter(position_id=filter_position)
    
    if filter_department:
        employees = employees.filter(department_id=filter_department)
    
    # Suppression de la pagination : on renvoie tous les employés filtrés
    positions = Position.objects.all()
    departments = Department.objects.all()

    context = {
        'page_title': 'Liste des Employés',
        'employees': employees,
        'positions': positions,
        'departments': departments,
        'filter_name': filter_name,
        'filter_position': filter_position,
        'filter_department': filter_department,
        'connected_employee': connected_employee,
    }
    
    return render(request, 'liste_employes.html', context)


def configuration(request):
    from .models.prime import Prime
    from .models.leave_type import LeaveType
    from .models.speciality import Speciality
    from .models.social_contribution import SocialContribution
    from .models.model_calcul import ModelCalcul
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        entity = request.POST.get('entity')
        action = request.POST.get('action')
        if entity == 'position':
            return handle_position_crud(request)
        elif entity == 'department':
            return handle_department_crud(request)
        elif entity == 'contract_type':
            return handle_contract_type_crud(request)
        elif entity == 'leave_type':
            return handle_leave_type_crud(request)
        elif entity == 'prime':
            return handle_prime_crud(request)
        elif entity == 'model_calcul':
            return handle_model_calcul_crud(request)
        elif entity == 'speciality':
            return handle_speciality_crud(request)
        elif entity == 'acte':
            return handle_acte_crud(request)
    positions = Position.objects.all()
    departments = Department.objects.all()
    contract_types = ContractType.objects.all()
    primes = Prime.objects.all()
    leave_types = LeaveType.objects.all()
    specialities = Speciality.objects.all()
    social_contributions = SocialContribution.objects.all()
    model_calculs = ModelCalcul.objects.all()
    actes = Acte.objects.all()
    context = {
        'page_title': 'Configuration RH',
        'positions': positions,
        'departments': departments,
        'contract_types': contract_types,
        'primes': primes,
        'leave_types': leave_types,
        'specialities': specialities,
        'social_contributions': social_contributions,
        'model_calculs': model_calculs,
        'actes': actes,
    }
    return render(request, 'hr_configuration.html', context)


def handle_position_crud(request):
    if request.method == 'POST' and request.POST.get('entity') == 'position':
        try:
            name = request.POST.get('name')
            pk = request.POST.get('pk')
            action = request.POST.get('action')
            
            # Validation des données
            if not name and action != 'delete':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Le nom du poste est requis'
                }, status=400)
                
            if action == 'delete' and pk:
                obj = get_object_or_404(Position, pk=pk)
                log_action(request.user, obj, 'suppression')
                obj.delete()
                return JsonResponse({
                    'status': 'success',
                    'message': f'Le poste "{obj.name}" a été supprimé avec succès'
                })
            elif action == 'edit' and pk:
                obj = get_object_or_404(Position, pk=pk)
                obj.name = name
                obj.save()
                log_action(request.user, obj, 'modification')
                log_action(request.user, obj, 'modification')
                return JsonResponse({
                    'status': 'success',
                    'message': f'Le poste "{name}" a été modifié avec succès'
                })
            elif action == 'add':
                obj = Position.objects.create(name=name)
                log_action(request.user, obj, 'creation')
                return JsonResponse({
                    'status': 'success',
                    'message': f'Le poste "{name}" a été ajouté avec succès'
                })
        except Exception as e:
            print(f"Erreur position CRUD: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Erreur lors du traitement de la demande: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Méthode non autorisée ou entité incorrecte'
    }, status=400)


def handle_department_crud(request):
    if request.method == 'POST' and request.POST.get('entity') == 'department':
        try:
            name = request.POST.get('name')
            pk = request.POST.get('pk')
            action = request.POST.get('action')
            parent_id = request.POST.get('parent')
            
            # Validation des données
            if not name and action != 'delete':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Le nom du département est requis'
                }, status=400)
                
            if action == 'delete' and pk:
                obj = get_object_or_404(Department, pk=pk)
                log_action(request.user, obj, 'suppression')
                obj.delete()
                return JsonResponse({
                    'status': 'success',
                    'message': f'Le département "{obj.name}" a été supprimé avec succès'
                })
            elif action == 'edit' and pk:
                obj = get_object_or_404(Department, pk=pk)
                obj.name = name
                
                # Gérer le parent
                if parent_id:
                    parent = get_object_or_404(Department, pk=parent_id)
                    obj.parent = parent
                else:
                    obj.parent = None
                    
                obj.save()
                log_action(request.user, obj, 'modification')
                return JsonResponse({
                    'status': 'success',
                    'message': f'Le département "{name}" a été modifié avec succès'
                })
            elif action == 'add':
                # Gérer le parent
                parent = None
                if parent_id:
                    parent = get_object_or_404(Department, pk=parent_id)
                
                # Créer le département sans spécifier d'ID (laisse Django gérer l'auto-increment)
                obj = Department.objects.create(name=name, parent=parent)
                log_action(request.user, obj, 'creation')
                return JsonResponse({
                    'status': 'success',
                    'message': f'Le département "{name}" a été ajouté avec succès',
                    'id': obj.id  # Retourner l'ID généré automatiquement
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Action non reconnue'
                }, status=400)
        except Exception as e:
            print(f"Erreur department CRUD: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Erreur lors du traitement de la demande: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Méthode non autorisée ou entité incorrecte'
    }, status=400)


def handle_contract_type_crud(request):
    if request.method == 'POST' and request.POST.get('entity') == 'contract_type':
        try:
            name = request.POST.get('name')
            pk = request.POST.get('pk')
            action = request.POST.get('action')
            
            # Validation des données
            if not name and action != 'delete':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Le nom du type de contrat est requis'
                }, status=400)
                
            if action == 'delete' and pk:
                obj = get_object_or_404(ContractType, pk=pk)
                log_action(request.user, obj, 'suppression')
                obj.delete()
                return JsonResponse({
                    'status': 'success',
                    'message': f'Le type de contrat "{obj.name}" a été supprimé avec succès'
                })
            elif action == 'edit' and pk:
                obj = get_object_or_404(ContractType, pk=pk)
                obj.name = name
                obj.save()
                log_action(request.user, obj, 'modification')
                return JsonResponse({
                    'status': 'success',
                    'message': f'Le type de contrat "{name}" a été modifié avec succès'
                })
            elif action == 'add':
                obj = ContractType.objects.create(name=name)
                log_action(request.user, obj, 'creation')
                return JsonResponse({
                    'status': 'success',
                    'message': f'Le type de contrat "{name}" a été ajouté avec succès'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Action non reconnue'
                }, status=400)
        except Exception as e:
            print(f"Erreur contract_type CRUD: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Erreur lors du traitement de la demande: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Méthode non autorisée ou entité incorrecte'
    }, status=400)


def handle_leave_type_crud(request):
    if request.method == 'POST' and request.POST.get('entity') == 'leave_type':
        try:
            # Log request for debugging
            print("Handling leave_type CRUD operation")
            print(f"POST data: {request.POST}")
            
            name = request.POST.get('name')
            default_days = request.POST.get('default_days')
            accrual_method = request.POST.get('accrual_method')
            description = request.POST.get('description', '')
            year = request.POST.get('year')
            
            # Jours de travail - convertir 'on'/'off' en booléen
            monday = request.POST.get('monday') == 'on'
            tuesday = request.POST.get('tuesday') == 'on'
            wednesday = request.POST.get('wednesday') == 'on'
            thursday = request.POST.get('thursday') == 'on'
            friday = request.POST.get('friday') == 'on'
            saturday = request.POST.get('saturday') == 'on'
            sunday = request.POST.get('sunday') == 'on'
            active = request.POST.get('active') == 'on'
            
            # Get ID value - accept either pk, type_id, or id
            pk = request.POST.get('pk') or request.POST.get('type_id') or request.POST.get('id')
            action = request.POST.get('action')
            
            print(f"Action: {action}, PK: {pk}, Name: {name}")
            print(f"Workdays: Mon={monday}, Tue={tuesday}, Wed={wednesday}, Thu={thursday}, Fri={friday}, Sat={saturday}, Sun={sunday}")
            print(f"Active: {active}")
            
            # Validation des données
            if not name and action != 'delete':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Le nom du type de congé est requis'
                }, status=400)
            
            try:
                if default_days and action != 'delete':
                    default_days = float(default_days.replace(',', '.'))
            except ValueError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Le nombre de jours doit être un nombre valide'
                }, status=400)
            
            if year and action != 'delete':
                try:
                    year = int(year)
                    if year < 2000 or year > 2100:
                        raise ValueError()
                except ValueError:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'L\'année doit être un nombre entre 2000 et 2100'
                    }, status=400)
            else:
                year = None
            
            if action == 'delete' and pk:
                print(f"Attempting to delete leave type with type_id: {pk}")
                # Utiliser type_id au lieu de pk pour chercher le type de congé
                try:
                    obj = LeaveType.objects.get(type_id=pk)
                    print(f"Found leave type: {obj}")
                    log_action(request.user, obj, 'suppression')
                    obj.delete()
                    print(f"Successfully deleted leave type")
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Type de congé supprimé avec succès'
                    })
                except LeaveType.DoesNotExist:
                    print(f"Leave type with type_id={pk} not found")
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Type de congé non trouvé'
                    }, status=404)
                except Exception as e:
                    print(f"Error deleting leave type: {str(e)}")
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Erreur lors de la suppression: {str(e)}'
                    }, status=500)
            
            elif action == 'edit' and pk:
                # Utiliser type_id au lieu de pk pour chercher le type de congé
                obj = get_object_or_404(LeaveType, type_id=pk)
                obj.name = name
                obj.default_days = default_days if default_days else None
                obj.accrual_method = accrual_method
                obj.description = description
                obj.year = year
                obj.active = active
                
                # Mise à jour des jours de travail
                obj.monday = monday
                obj.tuesday = tuesday
                obj.wednesday = wednesday
                obj.thursday = thursday
                obj.friday = friday
                obj.saturday = saturday
                obj.sunday = sunday
                
                obj.save()
                log_action(request.user, obj, 'modification')
                return JsonResponse({
                    'status': 'success',
                    'message': 'Type de congé modifié avec succès'
                })
            
            elif action == 'add':
                obj = LeaveType.objects.create(
                    name=name,
                    default_days=default_days if default_days else None,
                    accrual_method=accrual_method,
                    description=description,
                    year=year,
                    active=active,
                    monday=monday,
                    tuesday=tuesday,
                    wednesday=wednesday,
                    thursday=thursday,
                    friday=friday,
                    saturday=saturday,
                    sunday=sunday
                )
                log_action(request.user, obj, 'creation')
                return JsonResponse({
                    'status': 'success',
                    'message': 'Type de congé créé avec succès'
                })
            
            else:
                print(f"Invalid action: {action}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Action non valide'
                }, status=400)
                
        except LeaveType.DoesNotExist:
            print(f"Leave type not found exception")
            return JsonResponse({
                'status': 'error',
                'message': 'Type de congé non trouvé'
            }, status=404)
            
        except Exception as e:
            print(f"Erreur leave_type CRUD: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Une erreur est survenue: {str(e)}'
            }, status=500)
    
    print(f"Request method or entity incorrect: {request.method}, {request.POST.get('entity', 'None')}")
    return JsonResponse({
        'status': 'error',
        'message': 'Méthode non autorisée ou entité incorrecte'
    }, status=400)


def gestion_conges(request):
    from .models.leave_type import LeaveType
    from .models.employee import Employee
    from .models.leave_request import LeaveRequest

    current_year = datetime.now().year
    selected_year = request.GET.get('year', '')
    selected_type = request.GET.get('type', '')

    leave_types = LeaveType.objects.filter(active=True)
    
    # Déterminer l'employé courant
    employee = None
    if request.user.is_authenticated and hasattr(request.user, 'employee'):
        employee = request.user.employee
    if not employee:
        # Fallback: premier employé (pour compat. anciennes démos)
        employee = Employee.objects.order_by('id').first()
    leave_requests = []
    if employee:
        leave_requests = LeaveRequest.objects.filter(employee=employee).order_by('-request_date')
        if selected_year:
            leave_requests = leave_requests.filter(start_date__year=selected_year)
        if selected_type:
            leave_requests = leave_requests.filter(leave_type__type_id=selected_type)

    # Récupérer les années uniques des demandes de congés pour le filtre
    years = LeaveRequest.objects.filter(employee=employee).dates('start_date', 'year', order='DESC')
    years = [d.year for d in years]

    context = {
        'page_title': 'Gestion des Congés',
        'leave_types': leave_types,
        'current_year': current_year,
        'leave_requests': leave_requests,
        'years': years,
        'selected_year': int(selected_year) if selected_year else None,
        'selected_type': selected_type,
    }
    return render(request, 'leave_management.html', context)


@require_POST
def submit_leave_request(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    try:
        from .models.employee import Employee
        # Récupérer l'employee_id depuis le POST, sinon prendre le premier employé de la base
        employee_id = request.POST.get('employee_id')
        if not employee_id:
            # Utiliser l'employé lié à l'utilisateur connecté, si disponible
            if request.user.is_authenticated and hasattr(request.user, 'employee') and request.user.employee:
                employee_id = request.user.employee.id
            else:
                # Fallback legacy : premier employé de la base (ancienne démo)
                first_employee = Employee.objects.order_by('id').first()
                if first_employee:
                    employee_id = first_employee.id
                else:
                    if is_ajax:
                        return JsonResponse({'status': 'error','message': 'Aucun employé disponible.'}, status=400)
                    else:
                        messages.error(request, 'Aucun employé disponible.')
                        return redirect('gestion_conges')
        leave_type_id = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        notes = request.POST.get('notes', '')
        selected_days = request.POST.get('selected_days', None)
        
        # Valider les données
        if not all([employee_id, leave_type_id, start_date, end_date]):
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Tous les champs requis doivent être remplis'
                }, status=400)
            else:
                messages.error(request, 'Tous les champs requis doivent être remplis')
                return redirect('gestion_conges')
        
        # Convertir les dates
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Utiliser une transaction atomique pour éviter les doublons
        with transaction.atomic():
            # Vérification de chevauchement de congé (avec verrouillage)
            overlapping_requests = LeaveRequest.objects.select_for_update().filter(
                employee_id=employee_id,
                status__in=['submitted', 'approved'],
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            if overlapping_requests.exists():
                overlap = overlapping_requests.first()
                message = f"Vous avez déjà une demande de congé du {overlap.start_date} au {overlap.end_date}. Veuillez modifier les dates."
                if is_ajax:
                    return JsonResponse({
                        'status': 'overlap',
                        'message': message,
                        'overlap_start': str(overlap.start_date),
                        'overlap_end': str(overlap.end_date)
                    }, status=400)
                else:
                    messages.error(request, message)
                    return redirect('gestion_conges')
            
            # Vérification supplémentaire pour éviter les doublons exacts
            existing_request = LeaveRequest.objects.filter(
                employee_id=employee_id,
                leave_type_id=leave_type_id,
                start_date=start_date,
                end_date=end_date,
                status__in=['submitted', 'approved']
            ).first()
            
            if existing_request:
                message = "Une demande identique existe déjà pour ces dates."
                if is_ajax:
                    return JsonResponse({
                        'status': 'error',
                        'message': message
                    }, status=400)
                else:
                    messages.error(request, message)
                    return redirect('gestion_conges')
        
        # Récupérer le solde de congés pour ce type
        leave_balance = LeaveBalance.objects.filter(
            employee_id=employee_id,
            leave_type_id=leave_type_id,
            year=datetime.now().year
        ).first()
        
        # Si aucun solde n'existe, créer un nouveau solde
        if not leave_balance:
            leave_type = LeaveType.objects.get(type_id=leave_type_id)
            default_days = leave_type.default_days or Decimal('0')
            
            leave_balance = LeaveBalance.objects.create(
                employee_id=employee_id,
                leave_type_id=leave_type_id,
                year=datetime.now().year,
                entitlement=default_days,
                taken=0,
                remaining=default_days
            )
        
        certificate = None
        if 'certificate' in request.FILES and request.FILES['certificate']:
            certificate = request.FILES['certificate']
            
        try:
            leave_request = LeaveRequest.objects.create(
                employee_id=employee_id,
                leave_type_id=leave_type_id,
                start_date=start_date,
                end_date=end_date,
                notes=notes,
                certificate=certificate,
                selected_days=selected_days if selected_days else None,
                status='submitted'  # Création directement soumise
            )
            
            # Récupérer le type de congé pour vérifier s'il s'agit d'un congé ouvert
            leave_type = LeaveType.objects.get(type_id=leave_type_id)
            is_open_leave = leave_type.default_days is None or leave_type.default_days == 0
            
            # Vérifier le solde seulement si ce n'est pas un congé ouvert
            if not is_open_leave and leave_request.duration > leave_balance.remaining:
                leave_request.delete()
                if is_ajax:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Solde de congés insuffisant. Il vous reste {leave_balance.remaining} jour(s) pour ce type de congé.'
                    }, status=400)
                else:
                    messages.error(request, f'Solde de congés insuffisant. Il vous reste {leave_balance.remaining} jour(s) pour ce type de congé.')
                    return redirect('gestion_conges')
            
            # Réponse en fonction du type de requête
            if is_ajax:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Demande de congé créée avec succès. Vous pouvez maintenant la soumettre.',
                    'request_id': leave_request.request_id
                })
            else:
                messages.success(request, 'Demande de congé créée avec succès. Vous pouvez maintenant la soumettre.')
                return redirect('gestion_conges')
                
        except Exception as e:
            print(f"Erreur lors de la création de la demande: {str(e)}")
            import traceback
            traceback.print_exc()
            
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Erreur lors de la création de la demande: {str(e)}'
                }, status=500)
            else:
                messages.error(request, f'Erreur lors de la création de la demande: {str(e)}')
                return redirect('gestion_conges')
                
    except Exception as e:
        print(f"Erreur générale lors de la soumission: {str(e)}")
        import traceback
        traceback.print_exc()
        
        if is_ajax:
            return JsonResponse({
                'status': 'error',
                'message': f'Erreur lors de la soumission de la demande: {str(e)}'
            }, status=500)
        else:
            messages.error(request, f'Erreur lors de la soumission de la demande: {str(e)}')
            return redirect('gestion_conges')


@require_POST
def submit_draft_request(request):
    """Soumettre une demande en brouillon"""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        request_id = request.POST.get('request_id')
        if not request_id:
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': 'ID de demande manquant'}, status=400)
            else:
                messages.error(request, 'ID de demande manquant')
                return redirect('gestion_conges')
        
        # Récupérer la demande
        try:
            leave_request = LeaveRequest.objects.get(request_id=request_id)
        except LeaveRequest.DoesNotExist:
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': 'Demande non trouvée'}, status=404)
            else:
                messages.error(request, 'Demande non trouvée')
                return redirect('gestion_conges')
        
        # Vérifier que la demande est en brouillon
        if leave_request.status != 'draft':
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': 'Cette demande ne peut plus être soumise'}, status=400)
            else:
                messages.error(request, 'Cette demande ne peut plus être soumise')
                return redirect('gestion_conges')
        
        # Vérifier les chevauchements avant soumission
        overlapping_requests = LeaveRequest.objects.filter(
            employee=leave_request.employee,
            status__in=['submitted', 'approved'],
            start_date__lte=leave_request.end_date,
            end_date__gte=leave_request.start_date
        ).exclude(request_id=request_id)
        
        if overlapping_requests.exists():
            overlap = overlapping_requests.first()
            message = f"Vous avez déjà une demande de congé du {overlap.start_date} au {overlap.end_date}."
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': message}, status=400)
            else:
                messages.error(request, message)
                return redirect('gestion_conges')
        
        # Soumettre la demande
        leave_request.status = 'submitted'
        leave_request.save()
        
        if is_ajax:
            return JsonResponse({
                'status': 'success',
                'message': 'Demande soumise avec succès'
            })
        else:
            messages.success(request, 'Demande soumise avec succès')
            return redirect('gestion_conges')
            
    except Exception as e:
        print(f"Erreur lors de la soumission: {str(e)}")
        if is_ajax:
            return JsonResponse({
                'status': 'error',
                'message': f'Erreur lors de la soumission: {str(e)}'
            }, status=500)
        else:
            messages.error(request, f'Erreur lors de la soumission: {str(e)}')
            return redirect('gestion_conges')


def approbation_conges(request):
    # Récupérer tous les départements pour le filtre
    departments = Department.objects.all()
    # Récupérer tous les employés pour le formulaire de création de demande
    employees = Employee.objects.all().order_by('full_name')
    # Récupérer tous les types de congés actifs
    leave_types = LeaveType.objects.filter(active=True)
    # Récupérer toutes les demandes de congés en attente
    leave_requests = LeaveRequest.objects.filter(status='submitted').select_related(
        'employee', 'employee__department', 'leave_type')

    # Filtrer selon le rôle :
    session_user = request.session.get('user') or {}
    is_hr_employee = session_user.get('is_hr_employee', False)
    is_supervisor_flag = session_user.get('is_supervisor', False)

    if not is_hr_employee and is_supervisor_flag:
        # Supervisseur non-RH : ne voir que les demandes des employés non superviseurs
        # de son propre département
        if request.user.is_authenticated and hasattr(request.user, 'employee') and request.user.employee:
            from django.db.models import Q
            dept = request.user.employee.department
            leave_requests = leave_requests.filter(employee__department=dept).filter(
                Q(employee__is_supervisor=0) | Q(employee=request.user.employee)
            )
    elif not is_hr_employee:
        # Employé standard – pas d'accès à l'approbation
        leave_requests = LeaveRequest.objects.none()

    leave_requests = leave_requests.order_by('-request_date')
    context = {
        'page_title': 'Approbation des Congés',
        'departments': departments,
        'leave_requests': leave_requests,
        'employees': employees,
        'leave_types': leave_types,
    }
    return render(request, 'leave_approval.html', context)


def manager_approval_conges(request):
    """Interface d'avis pour les chefs de département."""
    # Vérif droit : uniquement superviseur non-RH
    session_user = request.session.get('user') or {}
    is_hr_employee = session_user.get('is_hr_employee', False)
    is_supervisor_flag = session_user.get('is_supervisor', False)
    # Access allowed for any supervisor (HR or non-HR). Non-supervisors are redirected.
    if not is_supervisor_flag:
        return redirect('gestion_conges')

    from .models.department import Department
    from django.db.models import Q
    departments = Department.objects.all()
    employees = Employee.objects.all().order_by('full_name')
    leave_types = LeaveType.objects.filter(active=True)

    leave_requests = LeaveRequest.objects.filter(status='submitted', manager_decision='pending').select_related(
        'employee', 'employee__department', 'leave_type'
    )

    # Filtrer sur le département du superviseur
    if request.user.is_authenticated and hasattr(request.user, 'employee') and request.user.employee:
        dept = request.user.employee.department
        leave_requests = leave_requests.filter(employee__department=dept).filter(
            Q(employee__is_supervisor=0) | Q(employee=request.user.employee)
        )

    context = {
        'page_title': 'Avis Chef Département',
        'departments': departments,
        'leave_requests': leave_requests,
        'employees': employees,
        'leave_types': leave_types,
    }
    return render(request, 'manager_approval.html', context)


@require_POST
def approve_leave_request(request, request_id):
    try:
        # Récupérer la demande de congé
        leave_request = LeaveRequest.objects.select_related('employee', 'leave_type').get(request_id=request_id)
        comments = request.POST.get('comments', '')
        # Vérifier si la demande peut être approuvée
        if leave_request.status != 'submitted':
            return JsonResponse({'status': 'error','message': 'Cette demande ne peut pas être approuvée (statut incorrect)'}, status=400)

        # Déterminer l'employé qui approuve
        approver_emp = None
        if request.user.is_authenticated and hasattr(request.user, 'employee') and request.user.employee:
            approver_emp = request.user.employee

        # Approuver la demande (la mise à jour du solde est gérée dans la méthode approve)
        if leave_request.approve(approver_emp, comments):
            return JsonResponse({
                'status': 'success',
                'message': 'Demande approuvée avec succès',
                'approval': {
                    'employee_name': approver_emp.full_name if approver_emp else None,
                    'decision_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'comments': comments
                }
            })
        else:
            return JsonResponse({'status': 'error','message': 'La demande ne peut pas être approuvée'}, status=400)
    except LeaveRequest.DoesNotExist:
        return JsonResponse({'status': 'error','message': 'Demande de congé non trouvée'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error','message': f'Erreur lors de l\'approbation: {str(e)}'}, status=500)


@require_POST
def manager_decision_leave_request(request, request_id):
    """Avis du chef de département (approve/refuse)."""
    from django.utils import timezone
    try:
        leave_request = LeaveRequest.objects.get(request_id=request_id)
        decision = request.POST.get('decision')  # 'approved' ou 'refused'
        comments = request.POST.get('comments', '')

        # Vérifications
        if decision not in ['approved', 'refused']:
            return JsonResponse({'status': 'error', 'message': 'Décision invalide'}, status=400)

        # Autorisation : seulement superviseur non-RH et dans même département
        session_user = request.session.get('user') or {}
        is_hr_employee = session_user.get('is_hr_employee', False)
        is_supervisor = session_user.get('is_supervisor', False)
        if not is_supervisor:
            return JsonResponse({'status': 'error', 'message': 'Seuls les superviseurs peuvent effectuer cette action'}, status=403)

        if request.user.is_authenticated and hasattr(request.user, 'employee') and request.user.employee:
            supervisor_emp = request.user.employee
            if supervisor_emp.department_id != leave_request.employee.department_id:
                return JsonResponse({'status': 'error', 'message': 'Vous ne pouvez pas donner un avis sur un autre département'}, status=403)
        else:
            return JsonResponse({'status': 'error', 'message': 'Utilisateur non lié à un employé'}, status=403)

        # Si déjà donné
        if leave_request.manager_decision != 'pending':
            return JsonResponse({'status': 'error', 'message': 'Avis déjà renseigné'}, status=400)

        # Enregistrer l'avis
        leave_request.manager_decision = decision
        leave_request.manager_decision_date = timezone.now()
        leave_request.manager_decider = supervisor_emp
        leave_request.manager_comments = comments
        leave_request.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Avis enregistré',
            'manager': {
                'decision': decision,
                'decision_date': leave_request.manager_decision_date.strftime('%Y-%m-%d %H:%M:%S'),
                'employee_name': supervisor_emp.full_name,
                'comments': comments
            }
        })
    except LeaveRequest.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Demande non trouvée'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': f'Erreur: {str(e)}'}, status=500)


@require_POST
def refuse_leave_request(request, request_id):
    try:
        leave_request = LeaveRequest.objects.get(request_id=request_id)
        comments = request.POST.get('comments', '')
        success = leave_request.refuse(None, comments)
        if success:
            return JsonResponse({'status': 'success','message': 'Demande refusée avec succès'})
        else:
            return JsonResponse({'status': 'error','message': 'La demande ne peut pas être refusée (statut incorrect)'})
    except LeaveRequest.DoesNotExist:
        return JsonResponse({'status': 'error','message': 'Demande de congé non trouvée'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error','message': f'Erreur lors du refus: {str(e)}'}, status=500)


@require_POST
def cancel_leave_request(request, request_id):
    try:
        leave_request = LeaveRequest.objects.get(request_id=request_id)
        if leave_request.status != 'submitted':
            return JsonResponse({'status': 'error','message': 'Cette demande ne peut pas être annulée.'}, status=400)
        leave_request.status = 'canceled'
        leave_request.save()
        return JsonResponse({'status': 'success','message': 'Demande annulée avec succès'})
    except LeaveRequest.DoesNotExist:
        return JsonResponse({'status': 'error','message': 'Demande de congé introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error','message': f'Erreur lors de l\'annulation de la demande: {str(e)}'}, status=500)


def get_leave_request(request, request_id):
    try:
        leave_request = LeaveRequest.objects.select_related('leave_type').get(request_id=request_id)
        request_data = {
            'request_id': leave_request.request_id,
            'leave_type': {'type_id': leave_request.leave_type.type_id,'name': leave_request.leave_type.name},
            'start_date': leave_request.start_date.strftime('%Y-%m-%d'),
            'end_date': leave_request.end_date.strftime('%Y-%m-%d'),
            'duration': float(leave_request.duration),
            'notes': leave_request.notes,
            'status': leave_request.status,
            'request_date': leave_request.request_date.strftime('%Y-%m-%d %H:%M:%S') if leave_request.request_date else None,
            'certificate': bool(leave_request.certificate),
            'certificate_name': leave_request.certificate.name.split('/')[-1] if leave_request.certificate else None,
            'certificate_url': leave_request.certificate.url if leave_request.certificate else None,
            'selected_days': leave_request.selected_days
        }
        try:
            approval = LeaveApproval.objects.select_related('employee').get(request=leave_request)
            request_data['approval'] = {
                'decision': approval.decision,
                'comments': approval.comments,
                'decision_date': approval.decision_date.strftime('%Y-%m-%d %H:%M:%S') if approval.decision_date else None,
                'employee_name': approval.employee.full_name if approval.employee else None
            }
        except LeaveApproval.DoesNotExist:
            request_data['approval'] = None
        return JsonResponse({'status': 'success','request': request_data})
    except LeaveRequest.DoesNotExist:
        return JsonResponse({'status': 'error','message': 'Demande de congé introuvable'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error','message': f'Erreur lors de la récupération de la demande: {str(e)}'}, status=500)


@require_POST
def edit_leave_request(request, request_id):
    try:
        leave_request = LeaveRequest.objects.get(request_id=request_id)
        if leave_request.status != 'submitted':
            return JsonResponse({'status': 'error','message': 'Cette demande ne peut pas être modifiée.'}, status=400)
        leave_type_id = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date') or start_date
        notes = request.POST.get('notes', '')
        selected_days = request.POST.get('selected_days', '')
        if not leave_type_id:
            return JsonResponse({'status': 'error','message': 'Veuillez sélectionner un type de congé'})
        if not start_date:
            return JsonResponse({'status': 'error','message': 'Veuillez sélectionner une date de début'})
        leave_request.leave_type_id = leave_type_id
        leave_request.start_date = start_date
        leave_request.end_date = end_date
        leave_request.notes = notes
        leave_request.selected_days = selected_days if selected_days else None
        if 'certificate' in request.FILES and request.FILES['certificate']:
            leave_request.certificate = request.FILES['certificate']
        leave_request.save()
        return JsonResponse({'status': 'success','message': 'Demande modifiée avec succès','request_id': leave_request.request_id})
    except LeaveRequest.DoesNotExist:
        return JsonResponse({'status': 'error','message': 'Demande de congé introuvable'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error','message': f'Erreur lors de la modification de la demande: {str(e)}'}, status=500)


@require_POST
def submit_draft_leave_request(request, request_id):
    # Vérifier si un employé est connecté
    if 'employee_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Non autorisé'}, status=401)
    
    try:
        # Récupérer la demande de congé
        employee_id = request.session.get('employee_id')
        leave_request = LeaveRequest.objects.get(
            request_id=request_id, 
            employee_id=employee_id
        )
        
        # Vérifier si la demande est en brouillon
        if leave_request.status != 'draft':
            return JsonResponse({
                'status': 'error',
                'message': 'Seules les demandes en brouillon peuvent être soumises'
            }, status=400)
        
        # Mettre à jour le statut de la demande
        leave_request.status = 'submitted'
        leave_request.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Demande de congé soumise avec succès',
            'request_id': leave_request.request_id
        })
        
    except LeaveRequest.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Demande de congé introuvable'
        }, status=404)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'message': f'Erreur lors de la soumission de la demande: {str(e)}'
        }, status=500)


@require_POST
def delete_leave_request(request, request_id):
    # Vérifier si un employé est connecté
    if 'employee_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Non autorisé'}, status=401)
    
    try:
        # Récupérer la demande de congé
        employee_id = request.session.get('employee_id')
        leave_request = LeaveRequest.objects.get(
            request_id=request_id, 
            employee_id=employee_id
        )
        
        # Vérifier si la demande peut être supprimée (seulement les demandes en brouillon)
        if leave_request.status != 'draft':
            return JsonResponse({
                'status': 'error',
                'message': 'Seules les demandes en brouillon peuvent être supprimées'
            }, status=400)
        
        # Supprimer la demande
        leave_request.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Demande de congé supprimée avec succès'
        })
        
    except LeaveRequest.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Demande de congé introuvable'
        }, status=404)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'message': f'Erreur lors de la suppression de la demande: {str(e)}'
        }, status=500)


def get_leave_request_details(request, request_id):
    # Suppression de la vérification de session pour accès sans login
    try:
        # Récupérer la demande de congé avec toutes les relations nécessaires
        leave_request = LeaveRequest.objects.select_related(
            'employee',
            'employee__department',
            'employee__position',
            'leave_type'
        ).get(request_id=request_id)
        # Récupérer l'approbation si elle existe
        try:
            approval = leave_request.approval
            if approval:
                approval_info = {
                    'employee_name': approval.employee.full_name,
                    'decision_date': approval.decision_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'comments': approval.comments
                }
            else:
                approval_info = None
        except:
            approval_info = None
        # Préparer la réponse
        response_data = {
            'status': 'success',
            'request': {
                'request_id': leave_request.request_id,
                'employee_name': leave_request.employee.full_name,
                'employee_department': leave_request.employee.department.name if leave_request.employee.department else None,
                'employee_position': leave_request.employee.position.name if leave_request.employee.position else None,
                'leave_type': leave_request.leave_type.name,
                'leave_type_id': leave_request.leave_type.type_id,
                'start_date': leave_request.start_date.strftime('%Y-%m-%d'),
                'end_date': leave_request.end_date.strftime('%Y-%m-%d'),
                'duration': str(leave_request.duration),
                'status': leave_request.status,
                'status_display': leave_request.get_status_display(),
                'request_date': leave_request.request_date.strftime('%Y-%m-%d %H:%M:%S'),
                'notes': leave_request.notes,
                'certificate_url': leave_request.certificate.url if leave_request.certificate else None,
                'certificate_name': leave_request.certificate.name.split('/')[-1] if leave_request.certificate else None,
                'approval': approval_info
            }
        }
        return JsonResponse(response_data)
    except LeaveRequest.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Demande de congé non trouvée'
        }, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'message': f'Erreur lors de la récupération des détails: {str(e)}'
        }, status=500)


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def calendar_conges(request):
    from .models.employee import Employee
    from .models.leave_request import LeaveRequest
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    months = []
    for i in range(6):
        month_number = (current_month + i - 1) % 12 + 1
        year = current_year + (current_month + i - 1) // 12
        month_name = {
            1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril', 5: 'Mai', 6: 'Juin',
            7: 'Juillet', 8: 'Août', 9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
        }[month_number]
        months.append({'number': month_number,'name': month_name,'year': year})
    holidays = []
    years_to_check = [current_year]
    if current_month > 6:
        years_to_check.append(current_year + 1)
    
    # Récupérer les filtres de requête
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')

    # Récupérer toutes les demandes de congés (tous employés confondus)
    leave_requests = LeaveRequest.objects.all()

    # Filtrage par statut
    if status_filter:
        leave_requests = leave_requests.filter(status=status_filter)

    # Filtrage par recherche (nom employé, type de congé, raison, etc.)
    if search_query:
        leave_requests = leave_requests.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(leave_type__name__icontains=search_query) |
            Q(reason__icontains=search_query)
        )

    # Ordonner par date de demande (plus récent en premier)
    leave_requests = leave_requests.order_by('-request_date')

    context = {
        'months': months,
        'holidays': holidays,
        'leave_requests': leave_requests,
        'selected_status': status_filter,
    }
    
    # Si c'est une requête AJAX, retourner seulement le contenu du tableau
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'calendar_history_table.html', context)
    
    return render(request, 'leave_calendar.html', context)


@require_GET
def get_calendar_events(request):
    from .models.employee import Employee
    from .models.leave_request import LeaveRequest
    from .models.holiday import Holiday
    # Récupérer toutes les demandes de congés approuvées pour tous les employés
    leave_requests = LeaveRequest.objects.filter(status='approved').select_related('leave_type', 'employee')
    # Formater les congés pour le calendrier
    leaves = []
    for leave_request in leave_requests:
        working_days = {
            0: leave_request.leave_type.sunday,
            1: leave_request.leave_type.monday,
            2: leave_request.leave_type.tuesday,
            3: leave_request.leave_type.wednesday,
            4: leave_request.leave_type.thursday,
            5: leave_request.leave_type.friday,
            6: leave_request.leave_type.saturday,
        }
        leaves.append({
            'id': leave_request.request_id,
            'employee_name': leave_request.employee.full_name,
            'leave_type': leave_request.leave_type.name,
            'start_date': leave_request.start_date.isoformat(),
            'end_date': leave_request.end_date.isoformat(),
            'duration': str(leave_request.duration),
            'working_days': working_days
        })
    # Jours fériés depuis la configuration (répliqués par année)
    current_year = datetime.now().year
    years = [current_year - 1, current_year, current_year + 1, current_year + 2]
    holidays = []
    for h in Holiday.objects.all():
        month = f"{h.date.month:02d}"
        day = f"{h.date.day:02d}"
        for y in years:
            holidays.append({'date': f"{y}-{month}-{day}", 'name': h.name})
    return JsonResponse({'status': 'success','leaves': leaves,'holidays': holidays})


def payroll_management(request):
    employees = Employee.objects.all().order_by('full_name')
    history_list = PayrollGenerationHistory.objects.select_related('employee', 'generated_by').order_by('-generated_at')

    # Filtres
    employee_id = request.GET.get('employee_id', '')
    search = request.GET.get('search', '').strip()
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    if employee_id:
        history_list = history_list.filter(employee_id=employee_id)
    if search:
        history_list = history_list.filter(employee__full_name__icontains=search)
    if start_date:
        history_list = history_list.filter(start_date__gte=start_date)
    if end_date:
        history_list = history_list.filter(end_date__lte=end_date)

    page_number = request.GET.get('page', 1)
    paginator = Paginator(history_list, 5)
    try:
        history = paginator.page(page_number)
    except PageNotAnInteger:
        history = paginator.page(1)
    except EmptyPage:
        history = paginator.page(paginator.num_pages)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'payroll_history_partial.html', {'history': history, 'employees': employees, 'filters': {
            'employee_id': employee_id,
            'search': search,
            'start_date': start_date,
            'end_date': end_date,
        }})

    from .models.leave_balance import LeaveBalance
    leave_balances = LeaveBalance.objects.filter(remaining__gt=0)
    return render(request, 'payroll_management.html', {
        'employees': employees,
        'history': history,
        'leave_balances': leave_balances,
        'filters': {
            'employee_id': employee_id,
            'search': search,
            'start_date': start_date,
            'end_date': end_date,
        }
    })

# CRUD SocialContribution
from django.views.decorators.http import require_POST

# Liste
def social_contribution_list(request):
    if 'employee_id' not in request.session:
        return redirect('employee_login')
    employee = Employee.objects.select_related('position').get(id=request.session['employee_id'])
    if not (employee.position.name == 'Ressources Humaines' or employee.is_supervisor):
        messages.error(request, "Accès réservé aux RH et RH responsables.")
        return redirect('human_resources')
    contributions = SocialContribution.objects.all()
    return render(request, 'social_contribution_list.html', {'contributions': contributions, 'connected_employee': employee})

# Création
@require_POST
def social_contribution_create(request):
    if 'employee_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Non autorisé'}, status=403)
    employee = Employee.objects.select_related('position').get(id=request.session['employee_id'])
    if not (employee.position.name == 'Ressources Humaines' or employee.is_supervisor):
        return JsonResponse({'status': 'error', 'message': 'Non autorisé'}, status=403)
    label = request.POST.get('label')
    rate = request.POST.get('rate')
    ceiling = request.POST.get('ceiling') or None
    contribution = SocialContribution.objects.create(label=label, rate=rate, ceiling=ceiling)
    return JsonResponse({'status': 'success', 'id': contribution.id})

# Modification
@require_GET
def employee_details(request, employee_id):
    """
    Vue AJAX pour récupérer les détails d'un employé
    """
    try:
        # Récupérer les détails de l'employé demandé
        employee = Employee.objects.select_related(
            'position', 
            'department', 
            'speciality',
            'model_calcul',
            'supervisor'
        ).prefetch_related('contracts__contract_type', 'children').get(id=employee_id)
        
        # Récupérer le type de contrat actuel (le plus récent)
        current_contract = employee.contracts.order_by('-id').first()
        contract_type_name = current_contract.contract_type.name if current_contract and current_contract.contract_type else 'Non défini'
        
        # Récupérer les informations détaillées des enfants
        children_details = []
        for child in employee.children.all():
            children_details.append({
                'name': child.name,
                'gender': dict(child.GENDER_CHOICES).get(child.gender, 'Non défini'),
                'birth_date': child.birth_date.strftime('%d/%m/%Y') if child.birth_date else 'Non défini',
                'is_scolarise': 'Oui' if child.is_scolarise else 'Non',
            })
        
        # Préparer les données de réponse
        data = {
            'status': 'success',
            'employee': {
                'id': employee.id,
                'employee_id': employee.employee_id,
                'national_id': employee.national_id,
                'full_name': employee.full_name,
                'position': employee.position.name if employee.position else 'Non défini',
                'department': employee.department.name if employee.department else 'Non défini',
                'contract_type': contract_type_name,
                'base_salary': float(employee.base_salary) if employee.base_salary else 0,
                'children_count': len(children_details),
                'birth_date': employee.birth_date.strftime('%d/%m/%Y') if employee.birth_date else 'Non défini',
                'photo_url': employee.photo.url if employee.photo else None,
                'speciality': employee.speciality.name if employee.speciality else 'Non défini',
                'email': employee.email or 'Non défini',
                'personal_phone': employee.personal_phone or 'Non défini',
                'work_phone': employee.work_phone or 'Non défini',
                'marital_status': dict(employee.MARITAL_STATUS_CHOICES).get(employee.marital_status, 'Non défini'),
                'gender': dict(employee.GENDER_CHOICES).get(employee.gender, 'Non défini'),
                'gender_raw': employee.gender,
                'status': dict(employee.STATUS_CHOICES).get(employee.status, 'Non défini'),
                'personal_address': employee.personal_address or 'Non défini',
                'work_address': employee.work_address or 'Non défini',
                'skills': employee.skills or 'Non défini',
                'career_evolution': employee.career_evolution or 'Non défini',
                'is_supervisor': 'Oui' if employee.is_supervisor else 'Non',
                'supervisor': employee.supervisor.full_name if employee.supervisor else 'Non défini',
                'model_calcul': employee.model_calcul.libelle if employee.model_calcul else 'Non défini',
                'children_details': children_details,
            }
        }
        
        return JsonResponse(data)
        
    except Employee.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Employé non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Erreur: {str(e)}'}, status=500)

# Modification
@require_POST
def social_contribution_update(request, pk):
    if 'employee_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Non autorisé'}, status=403)
    employee = Employee.objects.select_related('position').get(id=request.session['employee_id'])
    if not (employee.position.name == 'Ressources Humaines' or employee.is_supervisor):
        return JsonResponse({'status': 'error', 'message': 'Non autorisé'}, status=403)
    try:
        contribution = SocialContribution.objects.get(id=pk)
        contribution.label = request.POST.get('label')
        contribution.rate = request.POST.get('rate')
        contribution.ceiling = request.POST.get('ceiling') or None
        contribution.save()
        return JsonResponse({'status': 'success'})
    except SocialContribution.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Not found'}, status=404)

# Suppression
@require_POST
def social_contribution_delete(request, pk):
    if 'employee_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Non autorisé'}, status=403)
    employee = Employee.objects.select_related('position').get(id=request.session['employee_id'])
    if not (employee.position.name == 'Ressources Humaines' or employee.is_supervisor):
        return JsonResponse({'status': 'error', 'message': 'Non autorisé'}, status=403)
    try:
        contribution = SocialContribution.objects.get(id=pk)
        contribution.delete()
        return JsonResponse({'status': 'success'})
    except SocialContribution.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Not found'}, status=404)
    
    
    


@require_POST
def handle_social_contribution_crud(request):
    if request.POST.get('entity') != 'social_contribution':
        return JsonResponse({'status': 'error', 'message': 'Entité incorrecte'}, status=400)
    action = request.POST.get('action')
    pk = request.POST.get('pk')
    label = request.POST.get('label')
    rate = request.POST.get('rate')
    ceiling = request.POST.get('ceiling') or None
    try:
        if action == 'add':
            if not label or not rate:
                return JsonResponse({'status': 'error', 'message': 'Libellé et pourcentage requis'}, status=400)
            contribution = SocialContribution.objects.create(label=label, rate=rate, ceiling=ceiling)
            log_action(request.user, contribution, 'creation')
            return JsonResponse({'status': 'success', 'message': 'Cotisation sociale ajoutée', 'id': contribution.id})
        elif action == 'edit' and pk:
            contribution = SocialContribution.objects.get(id=pk)
            contribution.label = label
            contribution.rate = rate
            contribution.ceiling = ceiling
            contribution.save()
            log_action(request.user, contribution, 'modification')
            return JsonResponse({'status': 'success', 'message': 'Cotisation sociale modifiée'})
        elif action == 'delete' and pk:
            contribution = SocialContribution.objects.get(id=pk)
            log_action(request.user, contribution, 'suppression')
            contribution.delete()
            return JsonResponse({'status': 'success', 'message': 'Cotisation sociale supprimée'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Action ou identifiant manquant'}, status=400)
    except SocialContribution.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Cotisation non trouvée'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Erreur: {str(e)}'}, status=500)

@require_POST
def handle_prime_crud(request):
    if request.POST.get('entity') != 'prime':
        return JsonResponse({'status': 'error', 'message': 'Entité incorrecte'}, status=400)
    action = request.POST.get('action')
    pk = request.POST.get('pk')
    libelle = request.POST.get('libelle')
    rate = request.POST.get('rate') or None
    amount = request.POST.get('amount') or None
    try:
        if action == 'add':
            if not libelle:
                return JsonResponse({'status': 'error', 'message': 'Le libellé est requis'}, status=400)
            prime = Prime.objects.create(libelle=libelle, rate=rate, amount=amount)
            log_action(request.user, prime, 'creation')
            return JsonResponse({'status': 'success', 'message': 'Prime ajoutée', 'id': prime.id})
        elif action == 'edit' and pk:
            prime = Prime.objects.get(id=pk)
            prime.libelle = libelle
            prime.rate = rate
            prime.amount = amount
            prime.save()
            log_action(request.user, prime, 'modification')
            return JsonResponse({'status': 'success', 'message': 'Prime modifiée'})
        elif action == 'delete' and pk:
            prime = Prime.objects.get(id=pk)
            log_action(request.user, prime, 'suppression')
            prime.delete()
            return JsonResponse({'status': 'success', 'message': 'Prime supprimée'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Action ou identifiant manquant'}, status=400)
    except Prime.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Prime non trouvée'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Erreur: {str(e)}'}, status=500)


@require_POST
def handle_model_calcul_crud(request):
    if request.POST.get('entity') != 'model_calcul':
        return JsonResponse({'status': 'error', 'message': 'Entité incorrecte'}, status=400)
    action = request.POST.get('action')
    pk = request.POST.get('pk')
    libelle = request.POST.get('name') or request.POST.get('libelle')
    try:
        if action == 'add':
            if not libelle:
                return JsonResponse({'status': 'error', 'message': 'Le libellé est requis'}, status=400)
            model_calcul = ModelCalcul.objects.create(libelle=libelle)
            log_action(request.user, model_calcul, 'creation')
            
            # Handle many-to-many relationships
            social_contributions_ids = request.POST.getlist('social_contributions')
            primes_ids = request.POST.getlist('primes')
            if social_contributions_ids:
                model_calcul.social_contributions.set(social_contributions_ids)
            if primes_ids:
                model_calcul.primes.set(primes_ids)
            
            return JsonResponse({'status': 'success', 'message': 'Modèle de calcul ajouté', 'id': model_calcul.id})
        elif action == 'edit' and pk:
            model_calcul = ModelCalcul.objects.get(id=pk)
            model_calcul.libelle = libelle
            model_calcul.save()
            log_action(request.user, model_calcul, 'modification')
            
            # Handle many-to-many relationships
            social_contributions_ids = request.POST.getlist('social_contributions')
            primes_ids = request.POST.getlist('primes')
            model_calcul.social_contributions.set(social_contributions_ids)
            model_calcul.primes.set(primes_ids)
            
            return JsonResponse({'status': 'success', 'message': 'Modèle de calcul modifié'})
        elif action == 'delete' and pk:
            model_calcul = ModelCalcul.objects.get(id=pk)
            log_action(request.user, model_calcul, 'suppression')
            model_calcul.delete()
            return JsonResponse({'status': 'success', 'message': 'Modèle de calcul supprimé'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Action ou identifiant manquant'}, status=400)
    except ModelCalcul.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Modèle de calcul non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Erreur: {str(e)}'}, status=500)


def handle_holiday_crud(request):
    from django.http import JsonResponse
    from .models.holiday import Holiday
    if request.method != 'POST' or request.POST.get('entity') != 'holiday':
        return JsonResponse({'status': 'error', 'message': 'Requête invalide'}, status=400)

    action = request.POST.get('action')
    pk = request.POST.get('pk')
    name = request.POST.get('name')
    date = request.POST.get('date')
    month = request.POST.get('month')
    day = request.POST.get('day')
    year = request.POST.get('year')

    try:
        if action == 'seed' and year:
            try:
                year_int = int(year)
            except ValueError:
                return JsonResponse({'status': 'error', 'message': 'Année invalide'}, status=400)

            created_count = 0
            # Fixed holidays
            from datetime import date as _date
            fixed = [
                (_date(year_int, 1, 1), "Nouvel An"),
                (_date(year_int, 1, 11), "Manifeste de l'Indépendance"),
                (_date(year_int, 5, 1), "Fête du Travail"),
                (_date(year_int, 7, 30), "Fête du Trône"),
                (_date(year_int, 8, 14), "Allégeance Oued Eddahab"),
                (_date(year_int, 8, 20), "Révolution du Roi et du Peuple"),
                (_date(year_int, 8, 21), "Fête de la Jeunesse"),
                (_date(year_int, 11, 6), "Marche Verte"),
                (_date(year_int, 11, 18), "Fête de l'Indépendance"),
            ]
            # Insert fixed
            for d, n in fixed:
                if not Holiday.objects.filter(date=d, name=n).exists():
                    Holiday.objects.create(date=d, name=n)
                    created_count += 1

            # Try islamic if available
            try:
                from hijri_converter import Gregorian, Hijri
                hijri_start_year = Gregorian(year_int, 1, 1).to_hijri().year
                hijri_end_year = Gregorian(year_int, 12, 31).to_hijri().year
                for hyear in range(min(hijri_start_year, hijri_end_year) - 1, max(hijri_start_year, hijri_end_year) + 2):
                    dates = [
                        (Hijri(hyear, 1, 1).to_gregorian().datetimedate, "Nouvel An de l'Hégire"),
                        (Hijri(hyear, 1, 10).to_gregorian().datetimedate, "Achoura"),
                        (Hijri(hyear, 3, 12).to_gregorian().datetimedate, "Naissance du Prophète"),
                        (Hijri(hyear, 10, 1).to_gregorian().datetimedate, "Aïd al-Fitr"),
                        (Hijri(hyear, 10, 2).to_gregorian().datetimedate, "Aïd al-Fitr (2e jour)"),
                        (Hijri(hyear, 12, 10).to_gregorian().datetimedate, "Aïd al-Adha"),
                        (Hijri(hyear, 12, 11).to_gregorian().datetimedate, "Aïd al-Adha (2e jour)"),
                    ]
                    for d, n in dates:
                        if d.year != year_int:
                            continue
                        if not Holiday.objects.filter(date=d, name=n).exists():
                            Holiday.objects.create(date=d, name=n)
                            created_count += 1
            except Exception:
                pass

            return JsonResponse({'status': 'success', 'message': f'{created_count} jours fériés insérés pour {year_int}.'})

        if action == 'add':
            if not name:
                return JsonResponse({'status': 'error', 'message': 'Nom requis'}, status=400)
            if (not month or not day) and not date:
                return JsonResponse({'status': 'error', 'message': 'Jour et mois requis'}, status=400)
            if not date:
                date = f"2000-{str(month).zfill(2)}-{str(day).zfill(2)}"
            obj = Holiday.objects.create(name=name, date=date)
            log_action(request.user, obj, 'creation')
            return JsonResponse({'status': 'success', 'message': 'Jour férié ajouté', 'id': obj.id})
        elif action == 'edit' and pk:
            obj = Holiday.objects.get(id=pk)
            if name is not None:
                obj.name = name
            if month and day:
                obj.date = f"2000-{str(month).zfill(2)}-{str(day).zfill(2)}"
            elif date is not None:
                obj.date = date
            obj.save()
            log_action(request.user, obj, 'modification')
            return JsonResponse({'status': 'success', 'message': 'Jour férié modifié'})
        elif action == 'delete' and pk:
            obj = Holiday.objects.get(id=pk)
            log_action(request.user, obj, 'suppression')
            obj.delete()
            return JsonResponse({'status': 'success', 'message': 'Jour férié supprimé'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Action ou identifiant manquant'}, status=400)
    except Holiday.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Jour férié non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Erreur: {str(e)}'}, status=500)


def hr_configuration(request):
    """
    View for HR configuration page.
    """
    if request.method == 'POST':
        # Handle AJAX POST requests by delegating to appropriate CRUD handlers
        entity = request.POST.get('entity')
        
        if entity == 'position':
            return handle_position_crud(request)
        elif entity == 'department':
            return handle_department_crud(request)
        elif entity == 'contract_type':
            return handle_contract_type_crud(request)
        elif entity == 'leave_type':
            return handle_leave_type_crud(request)
        elif entity == 'prime':
            return handle_prime_crud(request)
        elif entity == 'social_contribution':
            return handle_social_contribution_crud(request)
        elif entity == 'speciality':
            return handle_speciality_crud(request)
        elif entity == 'model_calcul':
            return handle_model_calcul_crud(request)
        elif entity == 'service':
            return handle_acte_crud(request)
        elif entity == 'holiday':
            return handle_holiday_crud(request)
        else:
            return JsonResponse({
                'status': 'error',
                'message': f'Entité non reconnue: {entity}'
            }, status=400)
    
    # GET request - render the configuration page with all data
    from .models.holiday import Holiday
    context = {
        'positions': Position.objects.all(),
        'departments': Department.objects.all(),
        'contract_types': ContractType.objects.all(),
        'leave_types': LeaveType.objects.all(),
        'primes': Prime.objects.all(),
        'social_contributions': SocialContribution.objects.all(),
        'specialities': Speciality.objects.all(),
        'model_calculs': ModelCalcul.objects.all(),
        'services': Acte.objects.all(),
        'actes': Acte.objects.all(),
        'holidays': Holiday.objects.all(),
    }
    return render(request, 'hr_configuration.html', context)

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF', status=500)
    return response

@csrf_exempt
def download_payroll_pdf(request):
    # Récupérer les paramètres depuis GET ou POST
    employee_id = request.GET.get('employee_id') or request.POST.get('employee_id')
    start_date = request.GET.get('start_date') or request.POST.get('start_date')
    end_date = request.GET.get('end_date') or request.POST.get('end_date')
    if not (employee_id and start_date and end_date):
        return HttpResponse('Paramètres manquants', status=400)

    # Calcul du nombre de mois (chaque tranche de 30 jours = 1 mois)
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    nb_days = (end_dt - start_dt).days + 1
    nb_months = max(1, ceil(nb_days / 30))

    # Récupérer l'employé
    from .models.employee import Employee
    from .models.model_calcul import ModelCalcul
    from .models.prime import Prime
    from .models.social_contribution import SocialContribution
    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return HttpResponse('Employé introuvable', status=404)

    # Récupérer le modèle de calcul associé à l'employé
    model_calcul = getattr(employee, 'model_calcul', None)
    if not model_calcul:
        return HttpResponse('Aucun modèle de calcul associé à cet employé', status=404)

    # --- SUPPRIMER les calculs globaux ici (ils seront faits après mois_details) ---
    # --- Générer la liste des mois de la période (mois calendaire, pas tranches de 30j) ---
    start_month_dt = start_dt.replace(day=1)
    if end_dt.day == 1:
        if end_dt.month == 1:
            end_month_dt = end_dt.replace(year=end_dt.year - 1, month=12)
        else:
            end_month_dt = end_dt.replace(month=end_dt.month - 1)
    else:
        end_month_dt = end_dt.replace(day=1)
    mois_fr = [
        '', 'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
        'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
    ]
    mois_details = []
    current_dt = start_month_dt
    while True:
        mois_nom = f"{mois_fr[current_dt.month]} {current_dt.year}"
        base_salary_m = employee.base_salary
        primes_m = []
        for prime in model_calcul.primes.all():
            amount = 0
            if prime.rate:
                amount = employee.base_salary * (prime.rate / 100)
            elif prime.amount:
                amount = prime.amount
            primes_m.append({
                'libelle': prime.libelle,
                'rate': prime.rate or '-',
                'amount': round(amount, 2)
            })
        cotisations_m = []
        for cot in model_calcul.social_contributions.all():
            amount = 0
            if cot.rate:
                amount = employee.base_salary * (cot.rate / 100)
            cotisations_m.append({
                'libelle': cot.label,
                'rate': cot.rate or '-',
                'amount': round(amount, 2)
            })
        total_plus_m = sum(p['amount'] for p in primes_m)
        total_moins_m = sum(c['amount'] for c in cotisations_m)
        net_imposable_m = round(base_salary_m + total_plus_m - total_moins_m, 2)
        cotisation_cimr_m = next((c['amount'] for c in cotisations_m if 'cimr' in c['libelle'].lower()), 0)
        deduction_fiscale_m = min(cotisation_cimr_m, net_imposable_m * Decimal('0.5'))
        tranches = [
            {'taux': Decimal('0.00'), 'min': Decimal('0'), 'max': Decimal('2500')},
            {'taux': Decimal('0.10'), 'min': Decimal('2500.09'), 'max': Decimal('4166.67')},
            {'taux': Decimal('0.20'), 'min': Decimal('4166.75'), 'max': Decimal('5000')},
            {'taux': Decimal('0.30'), 'min': Decimal('5000.09'), 'max': Decimal('6666.67')},
            {'taux': Decimal('0.34'), 'min': Decimal('6666.75'), 'max': Decimal('15000')},
            {'taux': Decimal('0.38'), 'min': Decimal('15001'), 'max': Decimal('1000000000')},
        ]
        impot_brut_m = Decimal('0')
        for tranche in tranches:
            bas = tranche['min']
            haut = tranche['max']
            if net_imposable_m > bas:
                montant_tranche = min(net_imposable_m, haut) - bas
                if montant_tranche > 0:
                    impot_brut_m += montant_tranche * tranche['taux']
        impot_brut_m = round(impot_brut_m, 2)
        impot_revenu_m = max(0, round(impot_brut_m - deduction_fiscale_m, 2))
        net_a_payer_m = round(net_imposable_m - impot_revenu_m, 2)
        total_primes = total_plus_m
        total_cotisations = total_moins_m
        mois_details.append({
            'mois': mois_nom,
            'base_salary': base_salary_m,
            'primes': primes_m,
            'cotisations': cotisations_m,
            'total_primes': total_primes,
            'total_cotisations': total_cotisations,
            'net_imposable': net_imposable_m,
            'impot_brut': impot_brut_m,
            'deduction_fiscale': deduction_fiscale_m,
            'impot_revenu': impot_revenu_m,
            'net_a_payer': net_a_payer_m,
        })
        if current_dt.year == end_month_dt.year and current_dt.month == end_month_dt.month:
            break
        if current_dt.month == 12:
            current_dt = current_dt.replace(year=current_dt.year + 1, month=1)
        else:
            current_dt = current_dt.replace(month=current_dt.month + 1)

    # --- Calculs globaux APRÈS la génération de mois_details ---
    nb_mois_reels = len(mois_details)
    base_salary = employee.base_salary * nb_mois_reels
    # Primes (plus)
    primes = []
    total_plus = 0
    for prime in model_calcul.primes.all():
        amount = 0
        if prime.rate:
            amount = employee.base_salary * (prime.rate / 100)
        elif prime.amount:
            amount = prime.amount
        amount = amount * nb_mois_reels
        primes.append({
            'libelle': prime.libelle,
            'rate': prime.rate or '-',
            'amount': round(amount, 2)
        })
        total_plus += amount
    # Cotisations sociales (moins)
    cotisations = []
    total_moins = 0
    for cot in model_calcul.social_contributions.all():
        amount = 0
        if cot.rate:
            amount = employee.base_salary * (cot.rate / 100)
        amount = amount * nb_mois_reels
        cotisations.append({
            'libelle': cot.label,
            'rate': cot.rate or '-',
            'amount': round(amount, 2)
        })
        total_moins += amount
    # Calcul du net imposable global
    net_imposable = round(base_salary + total_plus - total_moins, 2)
    # 1. Trouver la cotisation CIMR (par libellé, insensible à la casse)
    cotisation_cimr = next((c['amount'] for c in cotisations if 'cimr' in c['libelle'].lower()), 0)
    # 2. Déduction fiscale
    # deduction_fiscale = min(cotisation_cimr, net_imposable * Decimal('0.5'))
    # 3. Calcul de l'impôt brut par tranches sur le net imposable global
    # ... (supprimer le calcul global de l'impôt, déduction, net à payer)
    # Utiliser la somme des valeurs mensuelles :
    impot_brut = sum(m['impot_brut'] for m in mois_details)
    deduction_fiscale = sum(m['deduction_fiscale'] for m in mois_details)
    impot_revenu = sum(m['impot_revenu'] for m in mois_details)
    net_a_payer = sum(m['net_a_payer'] for m in mois_details)
    # 4. Impôt sur le revenu
    # ... (supprimer le calcul global de l'impôt, déduction, net à payer)
    # Utiliser la somme des valeurs mensuelles :
    impot_revenu = sum(m['impot_revenu'] for m in mois_details)
    # 5. Net à payer global
    # ... (supprimer le calcul global de l'impôt, déduction, net à payer)
    # Utiliser la somme des valeurs mensuelles :
    net_a_payer = sum(m['net_a_payer'] for m in mois_details)

    context = {
        'employee': employee,
        'start_date': start_date,
        'end_date': end_date,
        'base_salary': base_salary,
        'primes': primes,
        'cotisations': cotisations,
        'net_imposable': net_imposable,
        'impot_brut': impot_brut,
        'deduction_fiscale': deduction_fiscale,
        'impot_revenu': impot_revenu,
        'net_salary': net_a_payer,  # net à payer = net_salary pour le PDF
        'net_a_payer': net_a_payer,
        'nb_months': nb_months,
    }
    context['mois_details'] = mois_details
    html_string = render_to_string('payroll_pdf.html', context)
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    # Log PDF generation action
    log_action(request.user, employee, 'impression')
    response['Content-Disposition'] = 'filename="bulletin_paie.pdf"'
    # Enregistrer l'historique de génération du bulletin de paie
    from .models.payroll_history import PayrollGenerationHistory
    rh_employee = None
    if request.user.is_authenticated:
        try:
            # Récupérer l'employé associé à l'utilisateur connecté
            rh_employee = Employee.objects.get(user=request.user)
        except Employee.DoesNotExist:
            # Gérer le cas où l'utilisateur n'a pas de profil employé
            rh_employee = None
    print(f"[DEBUG] Enregistrement historique: employee={employee}, generated_by={rh_employee}, start_date={start_date}, end_date={end_date}")
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        PayrollGenerationHistory.objects.create(
            employee=employee,
            generated_by=rh_employee,
            start_date=start_date_obj,
            end_date=end_date_obj
        )
        print(f"[SUCCESS] Historique enregistré: {employee.full_name} - {start_date} à {end_date}")
    except Exception as e:
        print(f"[ERREUR] Impossible d'enregistrer l'historique: {e}")
    return response

def payroll_history(request):
    if 'employee_id' not in request.session:
        return redirect('employee_login')
    employee_id = request.session.get('employee_id')
    employee = Employee.objects.select_related('position').get(id=employee_id)
    if not (employee.position.name == 'Ressources Humaines' or employee.is_supervisor):
        messages.error(request, "Accès réservé aux RH et RH responsables.")
        return redirect('human_resources')
    history = PayrollGenerationHistory.objects.select_related('employee', 'generated_by').order_by('-generated_at')
    return render(request, 'hr_templates/payroll_history.html', {
        'connected_employee': employee,
        'history': history,
    })

def handle_speciality_crud(request):
    from django.http import JsonResponse
    from .models.speciality import Speciality
    
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)
    
    try:
        # Récupérer les données de la requête
        data = request.POST
        action = data.get('action')
        entity = data.get('entity')
        pk = data.get('pk')
        name = data.get('name')
        
        # Vérifier que l'entité est bien 'speciality'
        if entity != 'speciality':
            return JsonResponse({'status': 'error', 'message': 'Entité non gérée'}, status=400)
        
        # Gérer les différentes actions
        if action == 'add':
            if not name:
                return JsonResponse({'status': 'error', 'message': 'Le nom de la spécialité est requis'}, status=400)
            speciality = Speciality.objects.create(name=name)
            log_action(request.user, speciality, 'creation')
            return JsonResponse({'status': 'success', 'message': 'Spécialité ajoutée avec succès', 'id': speciality.id})
            
        elif action == 'edit' and pk:
            if not name:
                return JsonResponse({'status': 'error', 'message': 'Le nom de la spécialité est requis'}, status=400)
            try:
                speciality = Speciality.objects.get(id=pk)
                speciality.name = name
                speciality.save()
                log_action(request.user, speciality, 'modification')
                return JsonResponse({'status': 'success', 'message': 'Spécialité modifiée avec succès'})
            except Speciality.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Spécialité non trouvée'}, status=404)
                
        elif action == 'delete' and pk:
            try:
                speciality = Speciality.objects.get(id=pk)
                log_action(request.user, speciality, 'suppression')
                speciality.delete()
                return JsonResponse({'status': 'success', 'message': 'Spécialité supprimée avec succès'})
            except Speciality.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Spécialité non trouvée'}, status=404)
        else:
            return JsonResponse({'status': 'error', 'message': 'Action non reconnue'}, status=400)
            
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Erreur: {str(e)}'}, status=500)


def handle_acte_crud(request):
    if request.method == 'POST' and request.POST.get('entity') == 'service':
        try:
            libelle = request.POST.get('libelle')
            price = request.POST.get('price')
            pk = request.POST.get('pk')
            action = request.POST.get('action')
            
            # Validation des données
            if not libelle and action != 'delete':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Le libellé de l\'acte est requis'
                }, status=400)
            
            if not price and action != 'delete':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Le prix de l\'acte est requis'
                }, status=400)
                
            if action == 'delete' and pk:
                obj = get_object_or_404(Acte, pk=pk)
                log_action(request.user, obj, 'suppression')
                obj.delete()
                return JsonResponse({
                    'status': 'success',
                    'message': f'L\'acte "{obj.libelle}" a été supprimé avec succès'
                })
            elif action == 'edit' and pk:
                obj = get_object_or_404(Acte, pk=pk)
                obj.libelle = libelle
                
                # Validation et conversion du prix
                try:
                    obj.price = Decimal(str(price).replace(',', '.'))
                except (ValueError, TypeError):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Le prix doit être un nombre valide'
                    }, status=400)
                    
                obj.save()
                log_action(request.user, obj, 'modification')
                return JsonResponse({
                    'status': 'success',
                    'message': f'L\'acte "{libelle}" a été modifié avec succès'
                })
            elif action == 'add':
                # Validation et conversion du prix
                try:
                    price_decimal = Decimal(str(price).replace(',', '.'))
                except (ValueError, TypeError):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Le prix doit être un nombre valide'
                    }, status=400)
                
                # Créer l'acte
                obj = Acte.objects.create(libelle=libelle, price=price_decimal)
                log_action(request.user, obj, 'creation')
                return JsonResponse({
                    'status': 'success',
                    'message': f'L\'acte "{libelle}" a été ajouté avec succès',
                    'id': obj.id  # Retourner l'ID généré automatiquement
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Action non reconnue'
                }, status=400)
        except Exception as e:
            print(f"Erreur acte CRUD: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Erreur lors du traitement de la demande: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Méthode non autorisée ou entité incorrecte'
    }, status=400)


@require_GET
def employee_details(request, employee_id):
    """
    Vue AJAX pour récupérer les détails d'un employé
    """
    try:
        # Récupérer les détails de l'employé demandé
        employee = Employee.objects.select_related(
            'position', 
            'department', 
            'speciality',
            'model_calcul',
            'supervisor'
        ).prefetch_related('contracts__contract_type', 'children').get(id=employee_id)
        
        # Récupérer le type de contrat actuel (le plus récent)
        current_contract = employee.contracts.order_by('-id').first()
        contract_type_name = current_contract.contract_type.name if current_contract and current_contract.contract_type else 'Non défini'
        # Récupérer les informations détaillées des enfants
        children_details = []
        for child in employee.children.all():
            children_details.append({
                'name': child.name,
                'gender': dict(child.GENDER_CHOICES).get(child.gender, 'Non défini'),
                'birth_date': child.birth_date.strftime('%d/%m/%Y') if child.birth_date else 'Non défini',
                'is_scolarise': 'Oui' if child.is_scolarise else 'Non',
            })
        
        # Préparer les données de réponse
        data = {
            'status': 'success',
            'employee': {
                'id': employee.id,
                'employee_id': employee.employee_id,
                'national_id': employee.national_id,
                'full_name': employee.full_name,
                'position': employee.position.name if employee.position else 'Non défini',
                'department': employee.department.name if employee.department else 'Non défini',
                'contract_type': contract_type_name,
                'base_salary': float(employee.base_salary) if employee.base_salary else 0,
                'children_count': len(children_details),
                'birth_date': employee.birth_date.strftime('%d/%m/%Y') if employee.birth_date else 'Non défini',
                'photo_url': employee.photo.url if employee.photo else None,
                'speciality': employee.speciality.name if employee.speciality else 'Non défini',
                'email': employee.email or 'Non défini',
                'personal_phone': employee.personal_phone or 'Non défini',
                'work_phone': employee.work_phone or 'Non défini',
                'marital_status': dict(employee.MARITAL_STATUS_CHOICES).get(employee.marital_status, 'Non défini'),
                'gender': dict(employee.GENDER_CHOICES).get(employee.gender, 'Non défini'),
                'gender_raw': employee.gender,  # Ajouter le genre brut pour le JavaScript
                'status': dict(employee.STATUS_CHOICES).get(employee.status, 'Non défini'),
                'personal_address': employee.personal_address or 'Non défini',
                'work_address': employee.work_address or 'Non défini',
                'skills': employee.skills or 'Non défini',
                'career_evolution': employee.career_evolution or 'Non défini',
                'is_supervisor': 'Oui' if employee.is_supervisor else 'Non',
                'supervisor': employee.supervisor.full_name if employee.supervisor else 'Non défini',
                'model_calcul': employee.model_calcul.libelle if employee.model_calcul else 'Non défini',
                'children_details': children_details,  # Ajouter les détails des enfants
            }
        }
        
        return JsonResponse(data)
        
    except Employee.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Employé non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Erreur: {str(e)}'}, status=500)



###################################### Gestion des sorties####################################################
from .models.sortie import Sortie
from django.views.decorators.http import require_POST
from django.db import transaction

def gestion_sorties(request):
    """Affiche la page de gestion des sorties"""
    sorties = Sortie.objects.all().order_by('-date_sortie')
    employees = Employee.objects.all().order_by('full_name')
    
    context = {
        'sorties': sorties,
        'employees': employees,
        'sortie_types': Sortie.TYPE_SORTIE
    }
    return render(request, 'gestion_sorties.html', context)

@require_POST
def ajouter_sortie(request):
    """Ajoute une nouvelle sortie"""
    try:
        with transaction.atomic():
            employe_nom = request.POST.get('employe_nom')
            type_sortie = request.POST.get('type_sortie')
            motif = request.POST.get('motif')
            date_sortie = request.POST.get('date_sortie')
            fichier = request.FILES.get('fichier')
            
            # Validation des données
            if not all([employe_nom, type_sortie, motif, date_sortie]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Tous les champs sont obligatoires'
                }, status=400)
            
            # Création de la sortie
            sortie = Sortie.objects.create(
                employe_nom=employe_nom,
                type_sortie=type_sortie,
                motif=motif,
                date_sortie=date_sortie,
                fichier=fichier
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Sortie enregistrée avec succès'
            })
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Erreur lors de l\'enregistrement: {str(e)}'
        }, status=500)

def modifier_sortie(request, sortie_id):
    """Modifie une sortie existante ou récupère ses données."""
    try:
        sortie = Sortie.objects.get(id=sortie_id)
    except Sortie.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Sortie non trouvée'}, status=404)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                sortie.employe_nom = request.POST.get('employe_nom', sortie.employe_nom)
                sortie.type_sortie = request.POST.get('type_sortie', sortie.type_sortie)
                sortie.motif = request.POST.get('motif', sortie.motif)
                sortie.date_sortie = request.POST.get('date_sortie', sortie.date_sortie)
                
                if 'fichier' in request.FILES:
                    sortie.fichier = request.FILES.get('fichier')
                
                sortie.save()
                return JsonResponse({'status': 'success', 'message': 'Sortie modifiée avec succès'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Erreur lors de la modification: {str(e)}'}, status=500)
    
    else: # GET request
        data = {
            'employe_nom': sortie.employe_nom,
            'type_sortie': sortie.type_sortie,
            'motif': sortie.motif,
            'date_sortie': sortie.date_sortie.strftime('%Y-%m-%d') if sortie.date_sortie else '',
            'fichier_url': sortie.fichier.url if sortie.fichier else ''
        }
        return JsonResponse({'status': 'success', 'data': data})

@require_POST
def supprimer_sortie(request, sortie_id):
    """Supprime une sortie"""
    try:
        with transaction.atomic():
            sortie = Sortie.objects.get(id=sortie_id)
            sortie.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Sortie supprimée avec succès'
            })
            
    except Sortie.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Sortie non trouvée'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Erreur lors de la suppression: {str(e)}'
        }, status=500)