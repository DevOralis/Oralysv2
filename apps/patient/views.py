from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Patient, EmergencyContact, Invoice, BillingHistory, Payment
from django.urls import reverse
from django.db.models import Q
from apps.hr.models.speciality import Speciality
from apps.hr.models.employee import Employee
from django_countries import countries
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
try:
    import weasyprint
except Exception:
    weasyprint = None
from .models import Appointment
from django.shortcuts import render, redirect
from django.urls import reverse
from apps.hr.models.employee import Employee
from .models import Patient
from .models import Consultation
import re
from django.http import JsonResponse
from django.core.paginator import Paginator
from apps.home.utils import log_action
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta, date
import json


@login_required
def billing_management(request):
    """Page de gestion des facturations - inspirée de payroll_management"""
    patients = Patient.objects.all().order_by('last_name', 'first_name')
    
    # Filtres
    search = request.GET.get('search', '')
    patient_id = request.GET.get('patient_id', '')
    
    # Historique des facturations - TOUTES les factures (payées et non payées)
    billing_history = BillingHistory.objects.all()
    
    if search:
        billing_history = billing_history.filter(
            Q(patient__first_name__icontains=search) |
            Q(patient__last_name__icontains=search)
        )
    
    if patient_id:
        billing_history = billing_history.filter(patient_id=patient_id)
    
    # Pagination
    paginator = Paginator(billing_history, 10)
    page_number = request.GET.get('page')
    billing_history = paginator.get_page(page_number)
    
    context = {
        'patients': patients,
        'billing_history': billing_history,
        'today': date.today(),
    }
    return render(request, 'billing_management.html', context)


def get_consultation_details(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id)
    return render(request, 'modal_consultation_details.html', {'c': consultation})

def get_appointment_details(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'modal_appointment_details.html', {'appointment': appointment})




def patient_list_create(request):
    # Gestion POST pour création/modification patient
    if request.method == 'POST':
        patient_id = request.POST.get('db_patient_id')
        next_url = request.POST.get('next')
        
        try:
            if patient_id:  # Modification
                patient = get_object_or_404(Patient, id=patient_id)
            else:  # Création
                patient = Patient()
            
            # Mise à jour des champs (noms correspondant au template)
            patient.patient_identifier = request.POST.get('patient_identifier', '')
            patient.last_name = request.POST.get('last_name', '')
            patient.first_name = request.POST.get('first_name', '')
            patient.cin = request.POST.get('cin', '')
            patient.passport_number = request.POST.get('passport_number', '')
            patient.email = request.POST.get('email', '')
            patient.gender = request.POST.get('gender', '')
            patient.birth_date = request.POST.get('birth_date') or None
            patient.nationality = request.POST.get('nationality', '')
            patient.city = request.POST.get('city', '')
            patient.phone = request.POST.get('phone', '')
            patient.mobile_number = request.POST.get('mobile_number', '')
            patient.address = request.POST.get('address', '')
            patient.profession = request.POST.get('profession', '')
            patient.spouse_name = request.POST.get('spouse_name', '')
            patient.situation_familiale = request.POST.get('situation_familiale', '')
            patient.disease_speciality = request.POST.get('disease_speciality', '')
            patient.treating_physician = request.POST.get('treating_physician', '')
            patient.referring_physician = request.POST.get('referring_physician', '')
            patient.nbr_enfants = request.POST.get('nbr_enfants') or 0
            patient.notes = request.POST.get('notes', '')
            patient.source = request.POST.get('source', '')
            patient.medical_notes = request.POST.get('medical_notes', '')
            # Champs assurance
            patient.has_insurance = request.POST.get('has_insurance') == '1'
            patient.insurance_number = request.POST.get('insurance_number', '')
            patient.affiliation_number = request.POST.get('affiliation_number', '')
            patient.relationship = request.POST.get('relationship', '')
            patient.insured_name = request.POST.get('insured_name', '')
            patient.save()
            
            # Gestion des documents médicaux
            medical_documents_count = int(request.POST.get('medical_documents_count', 0))
            if medical_documents_count > 0:
                from .models import MedicalDocument, DocumentType
                for i in range(medical_documents_count):
                    doc_type_code = request.POST.get(f'medical_document_type_{i}')
                    doc_file = request.FILES.get(f'medical_document_file_{i}')
                    
                    if doc_type_code and doc_file:
                        try:
                            # Récupérer le DocumentType par son code
                            doc_type = DocumentType.objects.get(code=doc_type_code, is_active=True)
                            MedicalDocument.objects.create(
                                patient=patient,
                                document_type=doc_type,
                                document_file=doc_file
                            )
                        except DocumentType.DoesNotExist:
                            # Si le type n'existe pas, on passe (ou on peut logger une erreur)
                            pass




            # Log action based on creation or modification
            if patient_id:
                log_action(request.user, patient, 'modification')
            else:
                log_action(request.user, patient, 'creation')
            
            # Gestion du contact d'urgence (relation ManyToMany)
            emergency_name = request.POST.get('emergency_name', '')
            emergency_phone = request.POST.get('emergency_phone', '')
            emergency_relationship = request.POST.get('emergency_relationship', '')
            
            if emergency_name or emergency_phone:
                # Récupérer ou créer le contact d'urgence
                emergency_contact = patient.emergency_contacts.first()
                if not emergency_contact:
                    # Créer un nouveau contact d'urgence
                    emergency_contact = EmergencyContact.objects.create(
                        name=emergency_name,
                        phone=emergency_phone,
                        relationship=emergency_relationship
                    )
                    log_action(request.user, emergency_contact, 'creation')
                    # L'ajouter à la relation ManyToMany
                    patient.emergency_contacts.add(emergency_contact)
                else:
                    # Mettre à jour le contact existant
                    emergency_contact.name = emergency_name
                    emergency_contact.phone = emergency_phone
                    emergency_contact.relationship = emergency_relationship
                    emergency_contact.save()
                    log_action(request.user, emergency_contact, 'modification')
            
            # Redirection selon next_url
            if next_url and 'complete_consultation' in next_url:
                return redirect(f"{next_url}?success=patient_updated")
            else:
                # Différencier le message selon l'action
                if patient_id:
                    return redirect(f"{reverse('patient:patient_list_create')}?success=patient_updated")
                else:
                    return redirect(f"{reverse('patient:patient_list_create')}?success=patient_created")
                
        except Exception as e:
            return redirect(f"{reverse('patient:patient_list_create')}?error={str(e)}")
    
    # Recherche et filtres AJAX
    search = request.GET.get('search', '').strip()
    medecin = request.GET.get('medecin', '').strip()
    patients = Patient.objects.all()
    if search:
        patients = patients.filter(
            Q(last_name__icontains=search) |
            Q(first_name__icontains=search) |
            Q(patient_identifier__icontains=search) |
            Q(cin__icontains=search) |
            Q(phone__icontains=search) |
            Q(mobile_number__icontains=search)
        )
    if medecin:
        patients = patients.filter(treating_physician=medecin)
    
    # Pagination - 5 patients par page
    page_number = request.GET.get('page', 1)
    paginator = Paginator(patients, 5)
    patients_page = paginator.get_page(page_number)

    # Pour modification
    patient = None
    patient_emergency_contact = None
    rdv = None
    if 'patient_id' in request.GET:
        patient = get_object_or_404(Patient, id=request.GET['patient_id'])
        # Pré-remplissage depuis le rendez-vous si besoin
        rdv_id = None
        next_url = request.GET.get('next')
        if next_url and 'complete_consultation' in next_url:
            # Extraire l'id du rdv depuis l'URL next
            match = re.search(r'complete_consultation/(\d+)', next_url)
            if match:
                rdv_id = match.group(1)
        if rdv_id:
            from .models import Appointment
            try:
                rdv = Appointment.objects.get(id=rdv_id)
                # Pour chaque champ vide du patient, remplir avec la valeur du rdv si dispo
                if not patient.last_name and rdv.nom:
                    patient.last_name = rdv.nom
                if not patient.first_name and rdv.prenom:
                    patient.first_name = rdv.prenom
                if not patient.phone and rdv.telephone:
                    patient.phone = rdv.telephone
                if not patient.email and rdv.email:
                    patient.email = rdv.email
            except Appointment.DoesNotExist:
                pass
        # On prend le premier contact d'urgence lié s'il existe
        if patient.emergency_contacts.exists():
            patient_emergency_contact = patient.emergency_contacts.first()

    consultation_url = None
    if 'next' in request.GET and 'complete_consultation' in request.GET['next']:
        consultation_url = request.GET['next']
    physicians = Employee.objects.filter(position__name__icontains="Médecin").select_related('speciality', 'position')
    emergency_contacts = EmergencyContact.objects.all()
    specialities = Speciality.objects.all()
    medecins = Employee.objects.filter(position__name__icontains="Médecin").select_related('speciality', 'position')
    
    # Récupérer les types de documents depuis la page Paramètres
    from .models import DocumentType, PatientSource
    document_types = DocumentType.objects.filter(is_active=True).order_by('name')
    
    # Récupérer les sources actives depuis la page Paramètres
    sources = PatientSource.objects.filter(is_active=True).order_by('name')
    
    context = {
        'patients': patients_page,
        'patient': patient,
        'patient_emergency_contact': patient_emergency_contact,
        'is_update': bool(patient and patient.id),
        'physicians': physicians,
        'emergency_contacts': emergency_contacts,
        'specialities': specialities,
        'medecins': medecins,
        'countries': list(countries),
        'paginator': paginator,
        'page_obj': patients_page,
        'consultation_url': consultation_url,
        'document_types': document_types,
        'sources': sources,  # Sources actives pour le formulaire
    }
    # Requête AJAX pour la pagination
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        from django.template.loader import render_to_string
        html = render_to_string('patient_table_partial.html', {
            'patients': patients_page,
            'paginator': paginator,
            'page_obj': patients_page,
            'request': request
        })
        from django.http import JsonResponse
        return JsonResponse({'html': html})
    return render(request, 'patient.html', context)


def delete_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    # Récupérer les contacts d'urgence liés avant suppression
    emergency_contacts = list(patient.emergency_contacts.all())
    try:
        log_action(request.user, patient, 'suppression')
        patient.delete()
        # Supprimer les EmergencyContact orphelins
        for contact in emergency_contacts:
            if contact.patient_set.count() == 0:
                log_action(request.user, contact, 'suppression')
                contact.delete()
        return redirect(reverse('patient:patient_list_create') + '?success=delete')
    except Exception as e:
        return redirect(reverse('patient:patient_list_create') + f'?error={e}')

def patient_pdf(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    emergency_contact = patient.emergency_contacts.first() if patient.emergency_contacts.exists() else None
    appointments_list = patient.appointments.order_by('-date_heure')
    consultations = patient.consultations.order_by('-date')
    html_string = render_to_string('patient_pdf.html', {
        'patient': patient,
        'emergency_contact': emergency_contact,
        'appointments_list': appointments_list,
        'consultations': consultations,
    })
    pdf = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="dossier_patient_{patient.last_name}_{patient.first_name}.pdf"'
    
    # Log PDF generation
    log_action(request.user, patient, 'impression')
    
    return response

def consultation(request):
    from apps.hr.models import Employee
    # Liste des médecins pour les filtres
    medecins = Employee.objects.filter(position__name__icontains="Médecin")
    
    # Récupérer les sources actives depuis la page paramètres
    from .models import PatientSource
    sources = PatientSource.objects.filter(is_active=True).order_by('name')
    
    # Recherche et filtres pour consultations à compléter
    search_todo = request.GET.get('search_todo', '').strip()
    filter_todo_medecin = request.GET.get('filter_todo_medecin', '').strip()
    appointments_qs = Appointment.objects.filter(statut='à venir').order_by('date_heure')
    if search_todo:
        appointments_qs = appointments_qs.filter(
            Q(patient__last_name__icontains=search_todo) |
            Q(patient__first_name__icontains=search_todo) |
            Q(nom__icontains=search_todo) |
            Q(prenom__icontains=search_todo) |
            Q(medecin__full_name__icontains=search_todo) |
            Q(motif__icontains=search_todo)
        )
    if filter_todo_medecin:
        appointments_qs = appointments_qs.filter(medecin_id=filter_todo_medecin)
    page_rdv = request.GET.get('page_rdv', 1)
    paginator_rdv = Paginator(appointments_qs, 5)
    appointments = paginator_rdv.get_page(page_rdv)

    # Recherche et filtres pour consultations validées
    search_done = request.GET.get('search_done', '').strip()
    filter_done_medecin = request.GET.get('filter_done_medecin', '').strip()
    consultations_qs = Consultation.objects.order_by('-date')
    if search_done:
        consultations_qs = consultations_qs.filter(
            Q(patient__last_name__icontains=search_done) |
            Q(patient__first_name__icontains=search_done) |
            Q(medecin__full_name__icontains=search_done) |
            Q(commentaires__icontains=search_done) |
            Q(traitement__icontains=search_done)
        )
    if filter_done_medecin:
        consultations_qs = consultations_qs.filter(medecin_id=filter_done_medecin)
    page_consult = request.GET.get('page_consult', 1)
    paginator_consult = Paginator(consultations_qs, 5)
    consultations = paginator_consult.get_page(page_consult)
    success = request.GET.get('success')
    error = request.GET.get('error')

    # Gestion AJAX pour pagination partielle
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        from django.template.loader import render_to_string
        from django.http import JsonResponse
        if 'page_rdv' in request.GET or 'search_todo' in request.GET or 'filter_todo_medecin' in request.GET:
            html = render_to_string('consultations_complete_partial.html', {
                'appointments': appointments,
                'paginator_rdv': paginator_rdv,
                'medecins': medecins,
                'search_todo': search_todo,
                'filter_todo_medecin': filter_todo_medecin,
            }, request=request)
            return JsonResponse({'html': html})
        elif 'page_consult' in request.GET or 'search_done' in request.GET or 'filter_done_medecin' in request.GET:
            html = render_to_string('consultations_valide_partial.html', {
                'consultations': consultations,
                'paginator_consult': paginator_consult,
                'medecins': medecins,
                'search_done': search_done,
                'filter_done_medecin': filter_done_medecin,
            }, request=request)
            return JsonResponse({'html': html})

    # Données pour le formulaire d'ajout
    from .models import Patient
    patients = Patient.objects.all().order_by('last_name', 'first_name')

    return render(request, 'consultation.html', {
        'appointments': appointments,
        'consultations': consultations,
        'paginator_rdv': paginator_rdv,
        'paginator_consult': paginator_consult,
        'success': success,
        'error': error,
        'medecins': medecins,
        'patients': patients,
        'sources': sources,  # Sources actives pour le formulaire
    })

def add_consultation(request):
    """Vue pour ajouter une nouvelle consultation (crée un rendez-vous à compléter)"""
    from .models import Patient, Appointment
    from apps.hr.models import Employee
    from django.contrib import messages
    from datetime import datetime
    
    if request.method == 'POST':
        try:
            # Récupération des données du formulaire
            is_existing = request.POST.get('is_existing', '0')
            patient_id = request.POST.get('patient_id')
            nom = request.POST.get('nom')
            prenom = request.POST.get('prenom')
            telephone = request.POST.get('telephone')
            email = request.POST.get('email')
            medecin_id = request.POST.get('medecin_id')
            date_heure = request.POST.get('date_heure')
            motif = request.POST.get('motif')
            source = request.POST.get('source', '')
            
            # Validation des champs requis
            if not medecin_id:
                messages.error(request, "Veuillez sélectionner un médecin")
                return redirect('patient:consultation')
            
            if not date_heure:
                messages.error(request, "Veuillez sélectionner une date et heure")
                return redirect('patient:consultation')
            
            if not motif:
                messages.error(request, "Veuillez saisir le motif de la consultation")
                return redirect('patient:consultation')
            
            # Gestion du patient
            patient = None
            if is_existing == '1' and patient_id:
                # Patient existant
                try:
                    patient = Patient.objects.get(id=patient_id)
                except Patient.DoesNotExist:
                    messages.error(request, "Patient sélectionné non trouvé")
                    return redirect('patient:consultation')
            else:
                # Nouveau patient - validation des champs requis
                if not nom or not prenom or not telephone or not email:
                    messages.error(request, "Veuillez remplir tous les champs obligatoires pour le nouveau patient")
                    return redirect('patient:consultation')
                
                # Créer le nouveau patient
                patient = Patient.objects.create(
                    last_name=nom,
                    first_name=prenom,
                    phone=telephone,
                    email=email,
                    source=source
                )
            
            # Récupération du médecin
            try:
                medecin = Employee.objects.get(id=medecin_id)
            except Employee.DoesNotExist:
                messages.error(request, "Médecin non trouvé")
                return redirect('patient:consultation')
            
            # Conversion de la date
            try:
                date_heure_obj = datetime.strptime(date_heure, '%Y-%m-%dT%H:%M')
            except ValueError:
                messages.error(request, "Format de date invalide")
                return redirect('patient:consultation')
            
            # Création du rendez-vous (qui apparaîtra dans "consultations à compléter")
            appointment = Appointment.objects.create(
                nom=nom if is_existing == '0' else patient.last_name,
                prenom=prenom if is_existing == '0' else patient.first_name,
                telephone=telephone if is_existing == '0' else patient.phone,
                email=email if is_existing == '0' else patient.email,
                patient=patient,
                medecin=medecin,
                date_heure=date_heure_obj,
                motif=motif,
                statut='à venir',  # Important : statut "à venir" pour apparaître dans "consultations à compléter"
                mode='direct'  # Valeur par défaut
            )
            
            messages.success(request, f'Rendez-vous créé avec succès pour {patient.last_name} {patient.first_name}')
            return redirect('patient:consultation')
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la création du rendez-vous: {str(e)}")
    
    return redirect('patient:consultation')

def admission_list(request):
    """Vue pour afficher la liste des admissions (urgences et planifiées)"""
    from .models import Consultation
    from django.db.models import Q
    from django.core.paginator import Paginator
    
    # Filtre par type d'admission
    type_admission_filter = request.GET.get('type_admission', '').strip()
    
    # Récupérer toutes les consultations avec hospitalisation = True
    consultations_qs = Consultation.objects.filter(
        hospitalisation=True
    ).select_related('patient', 'medecin').order_by('-date')
    
    # Appliquer le filtre par type d'admission
    if type_admission_filter == 'immediate':
        consultations_qs = consultations_qs.filter(type_admission='immediate')
    elif type_admission_filter == 'programmee':
        consultations_qs = consultations_qs.filter(type_admission='programmee')
    elif type_admission_filter == 'without_type':
        consultations_qs = consultations_qs.filter(
            Q(type_admission__isnull=True) | Q(type_admission='')
        )
    
    # Pagination
    paginator = Paginator(consultations_qs, 10)
    page = request.GET.get('page')
    consultations = paginator.get_page(page)
    
    return render(request, 'admission_list.html', {
        'consultations': consultations,
        'paginator': paginator,
        'type_admission_filter': type_admission_filter,
    })

def delete_admission(request, consultation_id):
    """Vue pour supprimer une admission (consultation avec hospitalisation)"""
    from django.http import JsonResponse
    from django.contrib import messages
    
    if request.method == 'POST':
        try:
            from .models import Consultation
            consultation = Consultation.objects.get(id=consultation_id, hospitalisation=True)
            patient_name = f"{consultation.patient.last_name} {consultation.patient.first_name}"
            
            # Supprimer la consultation
            consultation.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Admission de {patient_name} supprimée avec succès'
            })
            
        except Consultation.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Admission non trouvée'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erreur lors de la suppression: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée'
    }, status=405)

def delete_appointment(request, appointment_id):
    """Vue pour supprimer un rendez-vous (consultation à compléter)"""
    from django.http import JsonResponse
    from .models import Appointment
    
    if request.method == 'POST':
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            patient_name = f"{appointment.patient.last_name if appointment.patient else appointment.nom} {appointment.patient.first_name if appointment.patient else appointment.prenom}"
            
            # Supprimer le rendez-vous
            appointment.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Rendez-vous de {patient_name} supprimé avec succès'
            })
            
        except Appointment.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Rendez-vous non trouvé'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erreur lors de la suppression: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée'
    }, status=405)

def delete_consultation(request, consultation_id):
    """Vue pour supprimer une consultation validée"""
    from django.http import JsonResponse
    from .models import Consultation
    
    if request.method == 'POST':
        try:
            consultation = Consultation.objects.get(id=consultation_id)
            patient_name = f"{consultation.patient.last_name} {consultation.patient.first_name}"
            
            # Supprimer la consultation
            consultation.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Consultation de {patient_name} supprimée avec succès'
            })
            
        except Consultation.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Consultation non trouvée'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erreur lors de la suppression: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée'
    }, status=405)

def delete_medical_document(request, document_id):
    """Vue pour supprimer un document médical"""
    from django.http import JsonResponse
    from .models import MedicalDocument
    import os
    
    if request.method == 'POST':
        try:
            document = MedicalDocument.objects.get(id=document_id)
            
            # Supprimer le fichier du système de fichiers
            if document.document_file:
                if os.path.isfile(document.document_file.path):
                    os.remove(document.document_file.path)
            
            # Supprimer l'entrée de la base de données
            document.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Document supprimé avec succès'
            })
            
        except MedicalDocument.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Document non trouvé'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erreur lors de la suppression: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée'
    }, status=405)

def complete_consultation(request, rdv_id):
    rdv = Appointment.objects.get(id=rdv_id)
    patient = rdv.patient
    
    # Vérifier si le patient existe
    if not patient:
        # Rediriger vers une page d'erreur ou créer un patient
        return redirect('patient:patient_list_create')
    if request.method == 'POST':
        consultation_url = request.POST.get('consultation_url')
        if consultation_url:
            url = consultation_url
            if '?' in url:
                url += '&patient_completed=1'
            else:
                url += '?patient_completed=1'
            return redirect(url)
        commentaires = request.POST.get('commentaires')
        traitement = request.POST.get('traitement')
        temperature = request.POST.get('temperature')
        pression = request.POST.get('pression')
        rythme_cardiaque = request.POST.get('rythme_cardiaque')
        hospitalisation = request.POST.get('hospitalisation', '0') == '1'  # Convertir en booléen
        consigne_alimentaire = request.POST.get('consigne_alimentaire', '')
        consigne_hebergement = request.POST.get('consigne_hebergement', '')
        demande_patient = request.POST.get('demande_patient', 'consultation_normale')  # Récupérer la demande du patient
        type_admission = request.POST.get('type_admission', '')  # Récupérer le type d'admission
        date_admission_programmee = request.POST.get('date_admission_programmee', '')  # Récupérer la date d'admission programmée
        actes_ids = request.POST.getlist('actes[]')  # Récupérer les actes sélectionnés (nouveau format)
        # Récupérer les données des prescriptions de médicaments
        medicaments_ids = request.POST.getlist('medicaments[]')
        doses = request.POST.getlist('doses[]')
        frequences = request.POST.getlist('frequences[]')
        durees = request.POST.getlist('durees[]')
        moments = request.POST.getlist('moments[]')
        quantites = request.POST.getlist('quantites[]')
        instructions = request.POST.getlist('instructions[]')
        
        # Traiter la date d'admission programmée
        date_admission_value = None
        if date_admission_programmee:
            try:
                from datetime import datetime
                date_admission_value = datetime.strptime(date_admission_programmee, '%Y-%m-%d').date()
            except ValueError:
                pass  # Si la date est invalide, on la laisse à None
        
        consultation = Consultation.objects.create(
            patient=rdv.patient,
            medecin=rdv.medecin,
            speciality=rdv.medecin.speciality if rdv.medecin and hasattr(rdv.medecin, 'speciality') else None,
            commentaires=commentaires,
            traitement=traitement,
            temperature=temperature or None,
            pression=pression,
            rythme_cardiaque=rythme_cardiaque or None,
            hospitalisation=hospitalisation,
            demande_patient=demande_patient,
            type_admission=type_admission if type_admission else None,
            date_admission_programmee=date_admission_value,
            consigne_alimentaire=consigne_alimentaire,
            consigne_hebergement=consigne_hebergement,
        )
        
        # Associer les actes sélectionnés à la consultation
        if actes_ids:
            from apps.patient.models.acte_therapeutique import ActeTherapeutique
            actes_selected = ActeTherapeutique.objects.filter(id__in=actes_ids)
            consultation.actes.set(actes_selected)
        
        # Créer les prescriptions de médicaments
        if medicaments_ids:
            from apps.pharmacy.models.product import PharmacyProduct
            from apps.patient.models.medication_prescription import MedicationPrescription
            
            # Traiter chaque prescription de médicament
            for i, medicament_id in enumerate(medicaments_ids):
                if medicament_id:  # Vérifier que le médicament est sélectionné
                    try:
                        medicament = PharmacyProduct.objects.get(product_id=medicament_id)
                        
                        # Récupérer les valeurs correspondantes (avec gestion des index)
                        dose = doses[i] if i < len(doses) else ''
                        frequence = frequences[i] if i < len(frequences) else ''
                        duree = durees[i] if i < len(durees) else ''
                        moment = moments[i] if i < len(moments) else ''
                        quantite = quantites[i] if i < len(quantites) else None
                        instruction = instructions[i] if i < len(instructions) else ''
                        
                        # Créer la prescription
                        MedicationPrescription.objects.create(
                            consultation=consultation,
                            medicament=medicament,
                            dose=dose,
                            frequence=frequence,
                            duree=duree,
                            moment=moment,
                            quantite_totale=int(quantite) if quantite else None,
                            instructions_supplementaires=instruction
                        )
                    except (PharmacyProduct.DoesNotExist, ValueError) as e:
                        # Ignorer les erreurs de médicaments non trouvés ou de conversion
                        continue
        log_action(request.user, consultation, 'creation')
        rdv.statut = 'effectué'
        rdv.save()
        log_action(request.user, rdv, 'modification')
        return redirect(f"{reverse('patient:consultation')}?success=consultation")
    from apps.patient.models.acte_therapeutique import ActeTherapeutique
    from apps.pharmacy.models.product import PharmacyProduct
    import json
    
    # Récupérer tous les actes thérapeutiques actifs disponibles (depuis la page Paramètres)
    actes = ActeTherapeutique.objects.filter(is_active=True).order_by('libelle')
    
    # Récupérer tous les médicaments disponibles
    medicaments = PharmacyProduct.objects.all().order_by('short_label')
    
    # Convertir les actes en JSON pour le JavaScript
    actes_json = json.dumps([{
        'id': acte.id,
        'libelle': acte.libelle,
        'price': float(acte.price)
    } for acte in actes])
    
    # Convertir les médicaments en JSON pour le JavaScript
    medicaments_json = json.dumps([{
        'product_id': medicament.product_id,
        'short_label': medicament.short_label,
        'unit_price': float(medicament.unit_price),
        'nombrepiece': medicament.nombrepiece,
        'uom_label': medicament.uom.label if medicament.uom else '',
        'uom_symbole': medicament.uom.symbole if medicament.uom else ''
    } for medicament in medicaments])
    
    return render(request, 'complete_consultation.html', {
        'appointment': rdv, 
        'actes': actes,
        'actes_json': actes_json,
        'medicaments': medicaments,
        'medicaments_json': medicaments_json
    })

def consultation_pdf(request, consultation_id):
    from django.template.loader import render_to_string
    from django.http import HttpResponse
    try:
        import weasyprint
    except Exception:
        weasyprint = None
    from .models import Consultation
    consultation = Consultation.objects.get(id=consultation_id)
    html_string = render_to_string('consultation_pdf.html', {
        'consultation': consultation,
    })
    if weasyprint:
        pdf = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="consultation_{consultation.patient.last_name}_{consultation.patient.first_name}_{consultation.date:%Y%m%d}.pdf"'
    else:
        # Fallback to HTML if WeasyPrint is unavailable
        response = HttpResponse(html_string)
    
    # Log PDF generation
    log_action(request.user, consultation, 'impression')
    
    return response

def medecin_appointments_json(request):
    from django.http import JsonResponse
    
    if request.method != 'GET':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
        
    medecin_id = request.GET.get('medecin_id')
    if not medecin_id:
        return JsonResponse([], safe=False)
    
    try:
        rdvs = Appointment.objects.filter(medecin_id=medecin_id)
        events = [{
            'id': rdv.id,
            'title': f"{rdv.nom} {rdv.prenom}" if not rdv.patient else f"{rdv.patient.last_name} {rdv.patient.first_name}",
            'patient_nom': f"{rdv.nom} {rdv.prenom}" if not rdv.patient else f"{rdv.patient.last_name} {rdv.patient.first_name}",
            'date_heure': rdv.date_heure.isoformat(),
            'start': rdv.date_heure.isoformat(),
            'end': rdv.date_heure.isoformat(),
            'description': rdv.motif or '',
            'statut': rdv.statut,
            'color': '#198754',  # Vert pour les rendez-vous à venir
        } for rdv in rdvs]
        
        return JsonResponse(events, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def appointment(request):
    """Nouvelle vue pour la gestion des rendez-vous avec la nouvelle nomenclature."""
    # Copie complète de la vue rendez_vous
    patients = Patient.objects.all()
    medecins = Employee.objects.filter(position__name__icontains="Médecin")
    selected_medecin_id = request.GET.get('medecin_id')
    rdv_error_message = None
    
    # Récupérer les sources actives depuis la page paramètres
    from .models import PatientSource
    sources = PatientSource.objects.filter(is_active=True).order_by('name')
    
    # Initialiser les données du formulaire (vides par défaut)
    form_data = {
        'patient_id': '',
        'nom': '',
        'prenom': '',
        'telephone': '',
        'email': '',
        'medecin_id': '',
        'date_heure': '',
        'motif': '',
        'mode': '',
        'source': '',
        'is_existing': '0',  # Par défaut "Non"
    }
    
    # Filtrage des rendez-vous par médecin si sélectionné
    if selected_medecin_id:
        appointments_qs = Appointment.objects.filter(medecin_id=selected_medecin_id).order_by('-date_heure')
    else:
        appointments_qs = Appointment.objects.order_by('-date_heure')
    # Pagination pour la liste des rendez-vous récents (5 par page)
    page_number = request.GET.get('page', 1)
    paginator = Paginator(appointments_qs, 5)
    appointments = paginator.get_page(page_number)
    # Créneaux occupés pour chaque médecin (dict)
    creneaux_occupees = {}
    for med in medecins:
        creneaux_occupees[med.id] = list(Appointment.objects.filter(medecin=med).values_list('date_heure', flat=True))
    
    if request.method == 'POST':
        # Récupérer et préserver les données du formulaire
        form_data.update({
            'patient_id': request.POST.get('patient_id', ''),
            'nom': request.POST.get('nom', ''),
            'prenom': request.POST.get('prenom', ''),
            'telephone': request.POST.get('telephone', ''),
            'email': request.POST.get('email', ''),
            'medecin_id': request.POST.get('medecin_id', ''),
            'date_heure': request.POST.get('date_heure', ''),
            'motif': request.POST.get('motif', ''),
            'mode': request.POST.get('mode', ''),
            'source': request.POST.get('source', ''),
            'is_existing': request.POST.get('is_existing', '0'),
        })
        
        patient_id = form_data['patient_id']
        nom = form_data['nom']
        prenom = form_data['prenom']
        telephone = form_data['telephone']
        email = form_data['email']
        medecin_id = form_data['medecin_id']
        date_heure = form_data['date_heure']
        motif = form_data['motif']
        mode = form_data['mode']
        source = form_data['source']
        
        # Vérification du créneau déjà occupé (avec prise en compte de la durée d'un rendez-vous de 1 heure)
        if medecin_id and date_heure:
            from datetime import timedelta, datetime
            from django.utils import timezone
            
            # Convertir la date_heure en objet datetime aware (avec timezone)
            start_time_naive = datetime.strptime(date_heure, "%Y-%m-%dT%H:%M")
            start_time = timezone.make_aware(start_time_naive)
            end_time = start_time + timedelta(hours=1)
            
            # Vérifier s'il y a un chevauchement avec un rendez-vous existant
            # Récupérer tous les rendez-vous du médecin pour cette journée
            rendez_vous_existants = Appointment.objects.filter(
                medecin_id=medecin_id,
                date_heure__date=start_time.date()
            )
            
            existe = False
            for rdv in rendez_vous_existants:
                rdv_start = rdv.date_heure
                rdv_end = rdv_start + timedelta(hours=1)
                
                # Vérifier le chevauchement : 
                # Nouveau RDV [start_time -> end_time] vs Existant [rdv_start -> rdv_end]
                if start_time < rdv_end and end_time > rdv_start:
                    existe = True
                    break
            
            if existe:
                rdv_error_message = "Ce créneau chevauche un rendez-vous existant pour ce médecin. Veuillez choisir une autre heure."
                # Arrêter l'exécution et afficher l'erreur
                return render(request, 'appointment.html', {
                    'patients': patients,
                    'medecins': medecins,
                    'appointments': appointments,
                    'selected_medecin_id': selected_medecin_id,
                    'creneaux_occupees': creneaux_occupees,
                    'paginator': paginator,
                    'rdv_error_message': rdv_error_message,
                    'form_data': form_data,
                    'sources': sources,  # Sources actives pour le formulaire
                })
        
        if not rdv_error_message:
            try:
                # Debug: Afficher les données reçues
                print(f"DEBUG - Données reçues:")
                print(f"  patient_id: {patient_id}")
                print(f"  nom: {nom}")
                print(f"  prenom: {prenom}")
                print(f"  medecin_id: {medecin_id}")
                print(f"  date_heure: {date_heure}")
                print(f"  motif: {motif}")
                print(f"  mode: {mode}")
                
                # Création ou association du patient
                patient = None
                if patient_id:
                    patient = Patient.objects.get(id=patient_id)
                    nom = patient.last_name
                    prenom = patient.first_name
                    telephone = patient.phone
                    email = patient.email
                    print(f"DEBUG - Patient existant trouvé: {patient}")
                elif nom and prenom:
                    patient = Patient.objects.create(last_name=nom, first_name=prenom, phone=telephone, email=email, source=source)
                    log_action(request.user, patient, 'creation')
                    print(f"DEBUG - Nouveau patient créé: {patient}")
                else:
                    # Erreur si ni patient existant ni nom/prénom fournis
                    rdv_error_message = "Veuillez sélectionner un patient existant ou saisir nom et prénom."
                    print(f"DEBUG - Erreur: {rdv_error_message}")
                    return render(request, 'appointment.html', {
                        'patients': patients,
                        'medecins': medecins,
                        'appointments': appointments,
                        'selected_medecin_id': selected_medecin_id,
                        'creneaux_occupees': creneaux_occupees,
                        'paginator': paginator,
                        'rdv_error_message': rdv_error_message,
                        'form_data': form_data,
                    })
                
                medecin = Employee.objects.get(id=medecin_id) if medecin_id else None
                print(f"DEBUG - Médecin trouvé: {medecin}")
                
                rdv = Appointment.objects.create(
                    patient=patient,
                    nom=nom,
                    prenom=prenom,
                    telephone=telephone,
                    email=email,
                    medecin=medecin,
                    date_heure=start_time,  # Utiliser start_time (timezone aware) au lieu de date_heure
                    motif=motif,
                    mode=mode
                )
                print(f"DEBUG - Rendez-vous créé avec succès: {rdv}")
                print(f"DEBUG - ID du rendez-vous: {rdv.id}")
                
                log_action(request.user, rdv, 'creation')
                # Rester sur la page rendez-vous avec message de succès
                return redirect(f"{reverse('patient:appointment')}?success=rdv_created&medecin_id={medecin_id}")
            except Exception as e:
                print(f"DEBUG - Erreur lors de la création: {e}")
                import traceback
                traceback.print_exc()
                return redirect(f"{reverse('patient:appointment')}?medecin_id={medecin_id}&error={e}")
    
    return render(request, 'appointment.html', {
        'patients': patients,
        'medecins': medecins,
        'doctors': medecins,  # Assurez-vous que les deux noms sont dans le contexte
        'appointments': appointments,
        'selected_medecin_id': selected_medecin_id,
        'creneaux_occupees': creneaux_occupees,
        'paginator': paginator,
        'rdv_error_message': rdv_error_message,
        'form_data': form_data,
        'sources': sources,  # Sources actives pour le formulaire
    })

def appointment_table(request):
    medecins = Employee.objects.filter(position__name__icontains="Médecin")
    search = request.GET.get('search_rdv', '').strip()
    medecin_id = request.GET.get('filter_rdv_medecin', '').strip()
    statut = request.GET.get('filter_rdv_statut', '').strip()
    appointments_qs = Appointment.objects.order_by('-date_heure')
    
    if search:
        appointments_qs = appointments_qs.filter(
            Q(patient__last_name__icontains=search) |
            Q(patient__first_name__icontains=search) |
            Q(nom__icontains=search) |
            Q(prenom__icontains=search) |
            Q(medecin__full_name__icontains=search) |
            Q(motif__icontains=search)
        )
    
    if medecin_id:
        appointments_qs = appointments_qs.filter(medecin_id=medecin_id)
    
    if statut:
        appointments_qs = appointments_qs.filter(statut=statut)
    
    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(appointments_qs, 5)
    appointments = paginator.get_page(page_number)
    
    # Préparer les données pour la réponse JSON si c'est une requête AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('appointment_table.html', {
            'appointments': appointments,
            'paginator': paginator,
            'medecins': medecins,
            'selected_medecin_id': medecin_id,
            'search_rdv': search,
            'filter_rdv_medecin': medecin_id,
            'filter_rdv_statut': statut,
        }, request=request)
        return JsonResponse({'html': html})
    
    # Sinon, rendre la page complète
    return render(request, 'appointment_table.html', {
        'appointments': appointments,
        'paginator': paginator,
        'medecins': medecins,
        'selected_medecin_id': medecin_id,
        'search_rdv': search,
        'filter_rdv_medecin': medecin_id,
        'filter_rdv_statut': statut,
    })

def insurance_records(request):
    search = request.GET.get('search_mutuelle', '').strip()
    patients = Patient.objects.filter(has_insurance=True)
    # Debug: print number of patients with insurance
    print(f"DEBUG: Total patients with insurance: {patients.count()}")
    if search:
        patients = patients.filter(
            Q(last_name__icontains=search) |
            Q(first_name__icontains=search) |
            Q(insurance_number__icontains=search) |
            Q(affiliation_number__icontains=search) |
            Q(insured_name__icontains=search)
        )
    # Préparer la liste des relations distinctes pour le filtre
    relations = (
        Patient.objects.filter(has_insurance=True)
        .exclude(relationship__isnull=True)
        .exclude(relationship__exact="")
        .values_list('relationship', flat=True)
        .distinct()
    )
    # Pagination pour le dossier mutuelle
    page_number = request.GET.get('page', 1)
    from django.core.paginator import Paginator
    paginator = Paginator(patients, 5)
    patients_page = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('insurance_records_table.html', {
            'patients': patients_page,
            'paginator': paginator,
            'search_mutuelle': search,
        }, request=request)
        return JsonResponse({'html': html})
    else:
        # Check for success parameter to show SweetAlert
        success = request.GET.get('success', None)
        return render(request, 'insurance_records.html', {
            'patients': patients_page,
            'paginator': paginator,
            'search_mutuelle': search,
            'success': success,
        })

def mutuelle_edit_form(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        try:
            patient.insurance_number = request.POST.get('insurance_number')
            patient.affiliation_number = request.POST.get('affiliation_number')
            patient.relationship = request.POST.get('relationship')
            patient.insured_name = request.POST.get('insured_name')
            patient.save()
            log_action(request.user, patient, 'modification')
            return redirect(reverse('insurance_records') + '?success=insurance_updated')
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    # GET: retourne le formulaire HTML partiel
    return render(request, 'insurance_edit_form.html', {'patient': patient})

def consultation_invoice_list(request):
    """Liste des consultations non facturées et factures existantes"""
    # Consultations déjà faites mais pas encore facturées
    consultations_non_facturees = Consultation.objects.filter(
        is_invoiced=False
    ).select_related('patient', 'medecin').prefetch_related('actes').order_by('-date')
    
    # Factures existantes
    factures_existantes = Invoice.objects.all().select_related('patient', 'consultation', 'consultation__medecin').order_by('-created_date')
    
    context = {
        'consultations_non_facturees': consultations_non_facturees,
        'factures_existantes': factures_existantes,
    }
    return render(request, 'consultation_invoice_list.html', context)

def create_consultation_invoice(request):
    """Vue pour créer une nouvelle consultation et sa facture"""
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        actes_ids = request.POST.getlist('actes')
        medecin_id = request.POST.get('medecin_id')
        commentaires = request.POST.get('commentaires', '')
        
        if not patient_id:
            messages.error(request, "Veuillez sélectionner un patient")
            return redirect('patient:create_consultation_invoice')
        
        if not actes_ids:
            messages.error(request, "Veuillez sélectionner au moins un acte")
            return redirect('patient:create_consultation_invoice')
            
        try:
            from .models import Invoice
            from apps.patient.models.acte_therapeutique import ActeTherapeutique
            from apps.hr.models.employee import Employee
            
            patient = get_object_or_404(Patient, id=patient_id)
            medecin = get_object_or_404(Employee, id=medecin_id) if medecin_id else None
            actes = ActeTherapeutique.objects.filter(id__in=actes_ids)
            
            # Créer la consultation
            consultation = Consultation.objects.create(
                patient=patient,
                medecin=medecin,
                commentaires=commentaires,
                is_invoiced=True  # Marquer comme facturée immédiatement
            )
            
            # Associer les actes
            consultation.actes.set(actes)
            
            # Créer la facture automatiquement
            invoice = Invoice.objects.create(
                patient=patient,
                consultation=consultation
            )
            
            log_action(request.user, consultation, 'creation')
            log_action(request.user, invoice, 'creation')
            
            messages.success(request, f'Consultation et facture créées avec succès (N° {invoice.invoice_number})')
            return redirect('patient:consultation_invoice_list')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création: {str(e)}')
            return redirect('patient:create_consultation_invoice')
    
    # GET - Afficher le formulaire
    patients = Patient.objects.all().order_by('last_name', 'first_name')
    medecins = Employee.objects.filter(position__name__icontains="Médecin")
    from apps.patient.models.acte_therapeutique import ActeTherapeutique
    # Récupérer tous les actes thérapeutiques actifs (gérés depuis la page Paramètres)
    actes = ActeTherapeutique.objects.filter(is_active=True).order_by('libelle')
    
    context = {
        'patients': patients,
        'medecins': medecins,
        'actes': actes,
    }
    
    return render(request, 'create_consultation_invoice.html', context)


def invoice_from_consultation(request, consultation_id):
    """Créer une facture à partir d'une consultation existante"""
    consultation = get_object_or_404(Consultation, id=consultation_id)
    
    if consultation.is_invoiced:
        messages.warning(request, "Cette consultation est déjà facturée")
        return redirect('patient:consultation_invoice_list')
    
    try:
        from .models import Invoice
        
        # Créer la facture
        invoice = Invoice.objects.create(
            patient=consultation.patient,
            consultation=consultation
        )
        
        # Marquer la consultation comme facturée
        consultation.is_invoiced = True
        consultation.save()
        
        log_action(request.user, invoice, 'creation')
        messages.success(request, f'Facture créée avec succès (N° {invoice.invoice_number})')
        
    except Exception as e:
        messages.error(request, f'Erreur lors de la création de la facture: {str(e)}')
    
    return redirect('patient:consultation_invoice_list')


def simple_invoice_form(request):
    """Formulaire simple de facturation: sélectionner patient -> voir détails consultations + hébergement -> générer facture"""
    from .models import Patient, Consultation
    from apps.hosting.models import Admission
    from django.db.models import Sum
    
    patients = Patient.objects.all().order_by('last_name', 'first_name')
    
    selected_patient = None
    consultations_non_facturees = None
    admissions_non_facturees = None
    total_amount = 0
    total_consultations = 0
    total_hebergement = 0
    
    if request.method == 'GET' and 'patient_id' in request.GET:
        patient_id = request.GET.get('patient_id')
        if patient_id:
            try:
                selected_patient = Patient.objects.get(id=patient_id)
                
                # Récupérer consultations non facturées
                consultations_non_facturees = Consultation.objects.filter(
                    patient=selected_patient,
                    is_invoiced=False
                )
                
                # Récupérer admissions non facturées
                admissions_non_facturees = Admission.objects.filter(
                    patient=selected_patient,
                    is_invoiced=False
                )
                
                # Calculer les montants
                total_consultations = sum(c.get_total_cost() for c in consultations_non_facturees)
                total_hebergement = sum(a.calculate_total_cost() for a in admissions_non_facturees)
                total_amount = total_consultations + total_hebergement
                
            except Patient.DoesNotExist:
                messages.error(request, "Patient non trouvé")
    
    context = {
        'patients': patients,
        'selected_patient': selected_patient,
        'consultations_non_facturees': consultations_non_facturees,
        'admissions_non_facturees': admissions_non_facturees,
        'total_consultations': total_consultations,
        'total_hebergement': total_hebergement,
        'total_amount': total_amount,
    }
    return render(request, 'simple_invoice_form.html', context)


def generate_patient_invoice(request, patient_id):
    """Générer une facture globale pour toutes les consultations non facturées d'un patient + hébergement"""
    from .models import Patient, Invoice, Consultation
    from apps.hosting.models import Admission
    
    if request.method != 'POST':
        return redirect('patient:simple_invoice_form')
    
    patient = get_object_or_404(Patient, id=patient_id)
    consultations_non_facturees = Consultation.objects.filter(
        patient=patient,
        is_invoiced=False
    )
    
    # Récupérer les admissions non facturées du patient
    admissions_non_facturees = Admission.objects.filter(
        patient=patient,
        is_invoiced=False
    )
    
    # Vérifier qu'il y a au moins des consultations ou hébergement à facturer
    if not consultations_non_facturees.exists() and not admissions_non_facturees.exists():
        messages.warning(request, f"Aucune consultation ou hébergement non facturé pour {patient}")
        return redirect('patient:simple_invoice_form')
    
    try:
        # Créer une facture (utiliser première consultation si disponible, sinon créer facture autonome)
        premiere_consultation = consultations_non_facturees.first() if consultations_non_facturees.exists() else None
        
        if premiere_consultation:
            invoice = Invoice.objects.create(
                patient=patient,
                consultation=premiere_consultation
            )
        else:
            # Créer facture sans consultation (hébergement uniquement)
            invoice = Invoice()
            invoice.patient = patient
            invoice.consultation = None
            invoice.save()
        
        # Marquer toutes les consultations comme facturées
        if consultations_non_facturees.exists():
            consultations_non_facturees.update(is_invoiced=True)
        
        # Marquer toutes les admissions comme facturées
        if admissions_non_facturees.exists():
            admissions_non_facturees.update(is_invoiced=True)
        
        # Calculer le montant total : consultations + hébergement
        total_consultations = sum(c.get_total_cost() for c in consultations_non_facturees) if consultations_non_facturees.exists() else 0
        total_hebergement = sum(a.calculate_total_cost() for a in admissions_non_facturees) if admissions_non_facturees.exists() else 0
        total_amount = total_consultations + total_hebergement
        
        invoice.total_amount = total_amount
        invoice.save()
        
        # Message de succès détaillé
        details = []
        if consultations_non_facturees.exists():
            details.append(f"{consultations_non_facturees.count()} consultation(s)")
        if admissions_non_facturees.exists():
            details.append(f"{admissions_non_facturees.count()} hébergement(s)")
        
        messages.success(request, f'Facture globale créée avec succès (N° {invoice.invoice_number}) - {total_amount} DH - {" + ".join(details)}')
        
        # Rediriger vers le PDF de la facture
        return redirect('patient:invoice_pdf', invoice_id=invoice.id)
        
    except Exception as e:
        messages.error(request, f'Erreur lors de la création de la facture: {str(e)}')
        return redirect('patient:simple_invoice_form')


def invoice_pdf(request, invoice_id):
    """Générer le PDF d'une facture globale (consultations + hébergement)"""
    from .models import Invoice
    from django.template.loader import render_to_string
    try:
        from weasyprint import HTML
    except Exception:
        HTML = None
    from apps.hosting.models import Admission
    from decimal import Decimal
    from datetime import datetime
    
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Récupérer les consultations facturées pour ce patient à la date de création de la facture
    consultations = Consultation.objects.filter(
        patient=invoice.patient,
        is_invoiced=True,
        date__date=invoice.created_date.date()
    ).prefetch_related('actes').order_by('date')
    
    # Récupérer les admissions facturées pour ce patient à la date de création de la facture  
    admissions = Admission.objects.filter(
        patient=invoice.patient,
        is_invoiced=True,
        admission_date=invoice.created_date.date()
    ).select_related('room', 'room__room_type').order_by('admission_date')
    
    # Calculer total HT
    total_ht = Decimal('0')
    
    # Calculer total consultations
    for consultation in consultations:
        for acte in consultation.actes.all():
            total_ht += acte.price
    
    # Calculer total hébergement
    for admission in admissions:
        total_ht += admission.calculate_total_cost()
    
    # Calcul de la TVA (20% par exemple)
    tva_rate = Decimal('0.20')
    tva_amount = total_ht * tva_rate
    total_ttc = total_ht + tva_amount
    
    context = {
        'invoice': invoice,
        'patient': invoice.patient,
        'consultation': invoice.consultation,
        'consultations': consultations,
        'admissions': admissions,
        'total_ht': total_ht,
        'tva_rate': tva_rate * 100,  # En pourcentage
        'tva_amount': tva_amount,
        'total_ttc': total_ttc,
        'today': timezone.now().date(),
    }
    
    # Rendu du template HTML
    html_string = render_to_string('invoice_pdf.html', context)
    
    # Génération du PDF
    pdf = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    
    # Réponse HTTP
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="facture_{invoice.invoice_number}_{invoice.patient.last_name}.pdf"'
    
    return response


@login_required
def generate_direct_patient_pdf(request, patient_id):
    """Génère directement le PDF d'une facture globale pour un patient"""
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        
        # Créer automatiquement la facture globale
        consultations_non_facturees = Consultation.objects.filter(
            patient=patient,
            is_invoiced=False
        ).prefetch_related('actes').order_by('date')
        
        admissions_non_facturees = Admission.objects.filter(
            patient=patient,
            is_invoiced=False
        ).select_related('room', 'room__room_type').order_by('admission_date')
        
        if not consultations_non_facturees.exists() and not admissions_non_facturees.exists():
            messages.warning(request, f"Aucune consultation ou hébergement non facturé trouvé pour {patient.last_name} {patient.first_name}")
            return redirect('patient:consultation_invoice_list')
        
        # Créer la facture automatiquement
        invoice = Invoice.objects.create(
            patient=patient,
            consultation=consultations_non_facturees.first() if consultations_non_facturees.exists() else None,
            status='sent',
            notes=f"Facture globale - {consultations_non_facturees.count()} consultation(s), {admissions_non_facturees.count()} hébergement(s)"
        )
        
        # Marquer consultations comme facturées
        consultations_non_facturees.update(is_invoiced=True)
        
        # Marquer admissions comme facturées
        admissions_non_facturees.update(is_invoiced=True)
        
        # Rediriger vers le PDF de la facture créée
        return redirect('patient:invoice_pdf', invoice_id=invoice.id)
        
    except Exception as e:
        messages.error(request, f"Erreur lors de la génération de la facture: {str(e)}")
        return redirect('patient:consultation_invoice_list')

@login_required
def invoice_from_consultation(request, consultation_id):
    """Créer une facture à partir d'une consultation spécifique"""
    consultation = get_object_or_404(Consultation, id=consultation_id)
    
    if consultation.is_invoiced:
        messages.warning(request, "Cette consultation a déjà été facturée.")
        return redirect('patient:consultation_invoice_list')
    
    # Créer la facture
    invoice = Invoice.objects.create(
        patient=consultation.patient,
        consultation=consultation,
        status='sent',
        notes=f"Consultation du {consultation.date.strftime('%d/%m/%Y')}"
    )
    
    # Marquer la consultation comme facturée
    consultation.is_invoiced = True
    consultation.save()
    
    messages.success(request, f"Facture {invoice.invoice_number} créée avec succès.")
    return redirect('patient:invoice_pdf', invoice_id=invoice.id)

def patient_statistics(request):
    """Vue pour afficher les statistiques des patients"""
    
    # Statistiques principales
    total_patients = Patient.objects.count()
    total_consultations = Consultation.objects.count()
    total_appointments = Appointment.objects.count()
    patients_with_insurance = Patient.objects.filter(has_insurance=True).count()
    
    # Rendez-vous par statut
    appointments_by_status = Appointment.objects.values('statut').annotate(
        count=Count('id')
    )
    
    # Patients par genre
    patients_by_gender = Patient.objects.values('gender').annotate(
        count=Count('id')
    ).exclude(gender__isnull=True)
    
    # Patients par ville (top 10)
    patients_by_city = Patient.objects.values('city').annotate(
        count=Count('id')
    ).exclude(city__isnull=True).exclude(city='').order_by('-count')[:10]
    
    # Consultations par mois (6 derniers mois)
    consultations_by_month = []
    for i in range(6):
        month_start = (timezone.now().replace(day=1) - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        count = Consultation.objects.filter(
            date__gte=month_start,
            date__lte=month_end
        ).count()
        
        consultations_by_month.append({
            'month_name': month_start.strftime('%B %Y'),
            'count': count
        })
    
    consultations_by_month.reverse()
    
    # Consultations par spécialité
    consultations_by_specialty = Consultation.objects.filter(
        speciality__isnull=False
    ).values('speciality__name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Patients récents (5 derniers)
    recent_patients = Patient.objects.order_by('-id')[:5]
    
    # Consultations récentes (5 dernières)
    recent_consultations = Consultation.objects.select_related(
        'patient', 'medecin', 'speciality'
    ).order_by('-date')[:5]
    
    # Rendez-vous à venir (5 prochains)
    upcoming_appointments = Appointment.objects.filter(
        date_heure__gte=timezone.now(),
        statut='à venir'
    ).select_related('patient', 'medecin').order_by('date_heure')[:5]
    
    # Patients avec assurance vs sans assurance
    patients_insurance_stats = [
        {'category': 'Avec assurance', 'count': patients_with_insurance},
        {'category': 'Sans assurance', 'count': total_patients - patients_with_insurance}
    ]
    
    # Préparer les données JSON pour les graphiques
    appointments_status_json = json.dumps([
        {'status': item['statut'], 'count': item['count']} 
        for item in appointments_by_status
    ])
    
    patients_gender_json = json.dumps([
        {'gender': 'H' if item['gender'] == 'H' else 'F' if item['gender'] == 'F' else 'Autre', 'count': item['count']} 
        for item in patients_by_gender
    ])
    
    patients_city_json = json.dumps([
        {'city': item['city'], 'count': item['count']} 
        for item in patients_by_city
    ])
    
    consultations_month_json = json.dumps([
        {'month_name': month['month_name'], 'count': month['count']} 
        for month in consultations_by_month
    ])
    
    # Données JSON pour assurance
    patients_insurance_json = json.dumps(patients_insurance_stats)
    
    # Consultations par spécialité (exemple vide pour l'instant)
    consultations_specialty_json = json.dumps([])
    
    context = {
        'total_patients': total_patients,
        'total_consultations': total_consultations,
        'total_appointments': total_appointments,
        'patients_with_insurance': patients_with_insurance,
        'appointments_by_status': appointments_by_status,
        'patients_by_gender': patients_by_gender,
        'patients_by_city': patients_by_city,
        'consultations_by_month': consultations_by_month,
        'upcoming_appointments': upcoming_appointments,
        'recent_patients': recent_patients,
        'recent_consultations': recent_consultations,
        'consultations_month_json': consultations_month_json,
        'consultations_specialty_json': consultations_specialty_json,
        'patients_insurance_json': patients_insurance_json,
        'appointments_status_json': appointments_status_json,
        'patients_gender_json': patients_gender_json,
        'patients_city_json': patients_city_json,
    }
    
    return render(request, 'patient_statistics.html', context)


@login_required
def generate_patient_invoice_pdf(request, patient_id):
    """Génère une facture PDF complète pour un patient avec toutes les dépenses"""
    from django.http import HttpResponse
    from django.template.loader import get_template
    try:
        from weasyprint import HTML, CSS
    except Exception:
        HTML = None
        CSS = None
    from django.conf import settings
    import os
    
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        
        # Récupérer toutes les consultations du patient
        consultations = Consultation.objects.filter(patient=patient).select_related(
            'medecin', 'medecin__speciality'
        ).prefetch_related('actes')
        
        # Récupérer tous les hébergements du patient
        from apps.hosting.models import Admission, Companion
        admissions = Admission.objects.filter(patient=patient).select_related('room', 'bed')
        companions = Companion.objects.filter(patient=patient).select_related('room')
        
        # Récupérer toutes les prescriptions de médicaments du patient
        from apps.patient.models.medication_prescription import MedicationPrescription
        medication_prescriptions = MedicationPrescription.objects.filter(
            consultation__patient=patient
        ).select_related('medicament', 'consultation').order_by('-consultation__date')
        
        # Calculer les coûts
        total_actes = sum(
            sum(acte.price for acte in consultation.actes.all()) 
            for consultation in consultations
        )
        
        total_medicaments = sum(prescription.total_cost for prescription in medication_prescriptions)
        total_hebergement = sum(admission.calculate_room_cost() for admission in admissions)
        total_accompagnant = sum(companion.cout_total or 0 for companion in companions)
        total_general = total_actes + total_medicaments + total_hebergement + total_accompagnant
        
        # Calculer TVA et total TTC
        from decimal import Decimal
        tva_amount = total_general * Decimal('0.2')
        total_ttc = total_general * Decimal('1.2')

        # Préparer le contexte pour le template PDF
        context = {
            'patient': patient,
            'consultations': consultations,
            'admissions': admissions,
            'companions': companions,
            'medication_prescriptions': medication_prescriptions,
            'total_cout': {
                'actes': total_actes,
                'medicaments': total_medicaments,
                'hebergement': total_hebergement,
                'accompagnant': total_accompagnant,
                'total': total_general,
                'tva': int(tva_amount),
                'ttc': int(total_ttc)
            },
            'today': timezone.now().date(),
        }
        
        # Générer le PDF
        template = get_template('patient_invoice_pdf.html')
        html_content = template.render(context)
        
        # Convertir en PDF si WeasyPrint disponible, sinon renvoyer HTML
        if HTML is not None:
            pdf_file = HTML(string=html_content, base_url=request.build_absolute_uri('/')).write_pdf()
        else:
            pdf_file = None
        
        # Sauvegarder l'historique de facturation
        billing_date = request.GET.get('billing_date')
        if billing_date:
            try:
                billing_date = timezone.datetime.strptime(billing_date, '%Y-%m-%d').date()
            except:
                billing_date = timezone.now().date()
        else:
            billing_date = timezone.now().date()
            
        # Calculer la date d'échéance (30 jours après la facturation)
        from datetime import timedelta
        due_date = billing_date + timedelta(days=30)
        
        billing_history = BillingHistory.objects.create(
            patient=patient,
            generated_by=request.user,
            generated_at=timezone.now(),
            total_amount=total_ttc,
            billing_date=billing_date,
            due_date=due_date,
            status='pending',  # Statut par défaut : en attente
            notes=f"Facture générée - Actes: {total_actes}DH, Médicaments: {total_medicaments}DH, Hébergement: {total_hebergement}DH, Accompagnant: {total_accompagnant}DH"
        )
        
        # Ajouter le numéro de facture au contexte
        context['invoice_number'] = billing_history.invoice_number
        
        # Régénérer le PDF avec le numéro de facture
        html_content = template.render(context)
        if HTML is not None:
            pdf_file = HTML(string=html_content, base_url=request.build_absolute_uri('/')).write_pdf()
        
        # Retourner la réponse
        if pdf_file is not None:
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="facture_patient_{patient.last_name}_{patient.first_name}.pdf"'
            return response
        else:
            # Fallback HTML si WeasyPrint non installé
            return HttpResponse(html_content)
        
    except Exception as e:
        from django.http import JsonResponse
        return JsonResponse({'error': f'Erreur lors de la génération du PDF: {str(e)}'}, status=500)

@login_required
@require_http_methods(["POST"])
def mark_bill_as_paid(request, bill_id):
    """Marquer une facture comme payée"""
    try:
        from django.http import JsonResponse
        from django.views.decorators.csrf import csrf_exempt
        from django.utils.decorators import method_decorator
        
        billing_history = get_object_or_404(BillingHistory, id=bill_id)
        
        # Vérifier si la facture n'est pas déjà payée
        if billing_history.status == 'paid':
            return JsonResponse({'success': False, 'error': 'Cette facture est déjà marquée comme payée.'})
        
        # Marquer comme payée
        billing_history.status = 'paid'
        billing_history.save()
        
        return JsonResponse({'success': True, 'message': 'Facture marquée comme payée avec succès.'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur lors du paiement: {str(e)}'})


@login_required
@require_http_methods(["POST"])
def process_payment(request, bill_id):
    """Traiter un paiement - paiement total ou partiel avec versements"""
    try:
        from django.http import JsonResponse
        from django.utils import timezone
        from decimal import Decimal
        from .models import PartialPayment
        
        billing_history = get_object_or_404(BillingHistory, id=bill_id)
        
        # Vérifier si la facture n'est pas déjà payée
        if billing_history.status == 'paid':
            return JsonResponse({'success': False, 'error': 'Cette facture est déjà marquée comme payée.'})
        
        # Récupérer les données communes du formulaire
        journal = request.POST.get('journal', '')
        payment_mode = request.POST.get('payment_mode', 'full')
        memo = request.POST.get('memo', billing_history.invoice_number)
        
        if payment_mode == 'partial':
            # Traitement du paiement partiel avec versements
            
            # Récupérer les données des versements
            partial_channels = request.POST.getlist('partial_channel[]')
            partial_amounts = request.POST.getlist('partial_amount[]')
            partial_payment_dates = request.POST.getlist('partial_payment_date[]')
            partial_due_dates = request.POST.getlist('partial_due_date[]')
            
            # Vérifier qu'il y a au moins un versement
            if not partial_amounts or len(partial_amounts) == 0:
                return JsonResponse({'success': False, 'error': 'Aucun versement spécifié pour le paiement partiel.'})
            
            # Calculer le total des versements
            total_partial = Decimal('0.00')
            for amount_str in partial_amounts:
                if amount_str:
                    total_partial += Decimal(amount_str)
            
            # Créer l'enregistrement de paiement principal
            payment = Payment.objects.create(
                billing_history=billing_history,
                journal=journal,
                payment_channel='',  # Non applicable pour paiement partiel
                payment_mode=payment_mode,
                amount=total_partial,
                payment_date=partial_payment_dates[0] if partial_payment_dates else timezone.now().date(),
                memo=memo,
                created_by=request.user
            )
            
            # Créer les versements partiels
            for i in range(len(partial_amounts)):
                if partial_amounts[i]:
                    PartialPayment.objects.create(
                        payment=payment,
                        payment_number=i + 1,
                        payment_channel=partial_channels[i] if i < len(partial_channels) else 'cash',
                        amount=Decimal(partial_amounts[i]),
                        payment_date=partial_payment_dates[i] if i < len(partial_payment_dates) else timezone.now().date(),
                        due_date=partial_due_dates[i] if i < len(partial_due_dates) else timezone.now().date()
                    )
            
            # Vérifier si le total des versements couvre le montant de la facture
            if total_partial >= billing_history.total_amount:
                billing_history.status = 'paid'
            else:
                billing_history.status = 'pending'
            
            billing_history.save()
            
            message = f'Paiement partiel enregistré avec succès: {len(partial_amounts)} versement(s) pour un total de {total_partial} DH.'
            if total_partial >= billing_history.total_amount:
                message += ' Facture marquée comme payée.'
            else:
                remaining = billing_history.total_amount - total_partial
                message += f' Montant restant à payer: {remaining} DH.'
            
            return JsonResponse({'success': True, 'message': message})
        
        else:
            # Traitement du paiement total
            payment_channel = request.POST.get('payment_channel', 'cash')
        amount = request.POST.get('amount', billing_history.total_amount)
        payment_date = request.POST.get('payment_date', timezone.now().date())
        
        # Créer l'enregistrement de paiement pour l'historique
        payment = Payment.objects.create(
            billing_history=billing_history,
            journal=journal,
            payment_channel=payment_channel,
            payment_mode=payment_mode,
            amount=amount,
            payment_date=payment_date,
            memo=memo,
            created_by=request.user
        )
        
        # Marquer la facture comme payée
        billing_history.status = 'paid'
        billing_history.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Paiement de {amount} DH enregistré avec succès pour la facture {billing_history.invoice_number}.'
        })
        
    except Exception as e:
        import traceback
        return JsonResponse({'success': False, 'error': f'Erreur lors de l\'enregistrement du paiement: {str(e)}', 'traceback': traceback.format_exc()})


@login_required
def payments_list(request):
    """Page de gestion des paiements - affiche les factures payées"""
    from django.db.models import Q
    
    # Récupérer tous les paiements avec leurs factures associées et versements partiels
    payments = Payment.objects.select_related('billing_history', 'billing_history__patient', 'created_by').prefetch_related('partial_payments').all()
    
    # Filtres
    search = request.GET.get('search', '')
    payment_channel = request.GET.get('payment_channel', '')
    payment_mode = request.GET.get('payment_mode', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if search:
        payments = payments.filter(
            Q(billing_history__patient__first_name__icontains=search) |
            Q(billing_history__patient__last_name__icontains=search) |
            Q(billing_history__invoice_number__icontains=search) |
            Q(memo__icontains=search)
        )
    
    if payment_channel:
        payments = payments.filter(payment_channel=payment_channel)
    
    if payment_mode:
        payments = payments.filter(payment_mode=payment_mode)
    
    if date_from:
        payments = payments.filter(payment_date__gte=date_from)
    
    if date_to:
        payments = payments.filter(payment_date__lte=date_to)
    
    # Pagination
    paginator = Paginator(payments, 15)
    page_number = request.GET.get('page')
    payments = paginator.get_page(page_number)
    
    context = {
        'payments': payments,
        'payment_channel_choices': Payment.PAYMENT_CHANNEL_CHOICES,
        'payment_mode_choices': Payment.PAYMENT_MODE_CHOICES,
        'today': date.today(),
    }
    return render(request, 'payments_list.html', context)


@login_required 
def patient_summary(request):
    """Résumé patient avec toutes ses consultations, hébergements et coûts."""
    from apps.patient.models.acte_therapeutique import ActeTherapeutique
    from decimal import Decimal
    
    # Tous les patients pour le dropdown
    patients = Patient.objects.all().order_by('last_name', 'first_name')
    
    selected_patient_id = request.GET.get('patient_id')
    selected_patient = None
    consultations = None
    admissions = None
    companions = None
    total_cout = None
    
    if selected_patient_id:
        try:
            selected_patient = Patient.objects.get(id=selected_patient_id)
            
            # Consultations du patient
            consultations = Consultation.objects.filter(
                patient=selected_patient
            ).select_related('medecin').prefetch_related('actes', 'medication_prescriptions__medicament').order_by('-date')
            
            # Hébergements du patient
            from apps.hosting.models.admission import Admission
            from apps.hosting.models.companion import Companion
            
            admissions = Admission.objects.filter(
                patient=selected_patient
            ).select_related('room', 'bed').order_by('-admission_date')
            
            # Accompagnants du patient
            companions = Companion.objects.filter(
                patient=selected_patient
            ).select_related('room').order_by('-accommodation_start_date')
            
            # Calcul des coûts totaux
            total_consultations = Decimal('0.00')
            total_actes = Decimal('0.00')
            total_medicaments = Decimal('0.00')
            total_hebergement = Decimal('0.00')
            total_accompagnant = Decimal('0.00')
            
            # Coûts consultations et actes
            for consultation in consultations:
                if consultation.actes.exists():
                    total_actes += sum(acte.price for acte in consultation.actes.all())
                
                # Coûts des médicaments prescrits
                for prescription in consultation.medication_prescriptions.all():
                    if prescription.quantite_totale and prescription.medicament.unit_price:
                        total_medicaments += Decimal(str(prescription.medicament.unit_price)) * prescription.quantite_totale
            
            # Coûts hébergement
            for admission in admissions:
                total_hebergement += admission.calculate_room_cost()
            
            # Coûts accompagnants  
            for companion in companions:
                if companion.accommodation_start_date and companion.accommodation_end_date:
                    nb_jours = (companion.accommodation_end_date - companion.accommodation_start_date).days
                    if nb_jours <= 0:
                        nb_jours = 1
                    try:
                        acte_accompagnant = ActeTherapeutique.objects.filter(
                            libelle__icontains='Accompagnant',
                            is_active=True
                        ).first()
                        if acte_accompagnant:
                            total_accompagnant += acte_accompagnant.price * nb_jours
                        else:
                            total_accompagnant += Decimal('50.00') * nb_jours
                    except ActeTherapeutique.DoesNotExist:
                        total_accompagnant += Decimal('50.00') * nb_jours
            
            total_cout = {
                'consultations': total_consultations,
                'actes': total_actes,
                'medicaments': total_medicaments,
                'hebergement': total_hebergement,
                'accompagnant': total_accompagnant,
                'total': total_consultations + total_actes + total_medicaments + total_hebergement + total_accompagnant
            }
            
        except (Patient.DoesNotExist, ImportError):
            selected_patient = None
    
    # Récupérer toutes les prescriptions de médicaments pour ce patient
    medication_prescriptions = []
    if selected_patient and consultations:
        from apps.patient.models.medication_prescription import MedicationPrescription
        medication_prescriptions = MedicationPrescription.objects.filter(
            consultation__patient=selected_patient
        ).select_related('medicament', 'consultation').order_by('-consultation__date')
    
    # Vérifier si une facture a déjà été générée pour ce patient
    has_invoice = False
    if selected_patient:
        has_invoice = BillingHistory.objects.filter(patient=selected_patient).exists()
    
    context = {
        'patients': patients,
        'selected_patient_id': selected_patient_id,
        'selected_patient': selected_patient,
        'consultations': consultations,
        'admissions': admissions,
        'companions': companions,
        'total_cout': total_cout,
        'medication_prescriptions': medication_prescriptions,
        'has_invoice': has_invoice,
    }
    
    return render(request, 'patient_summary.html', context)


@login_required
def acte_list(request):
    """Vue pour la gestion des actes - Redirige vers la page Paramètres"""
    # Rediriger vers la page de configuration des paramètres (onglet actes)
    messages.info(request, 'La gestion des actes a été déplacée vers la page Paramètres.')
    return redirect('patient:patient_settings')


@login_required
def payment_details_json(request, payment_id):
    """Retourner les détails d'un paiement en JSON pour AJAX"""
    try:
        from django.http import JsonResponse
        from django.core.serializers.json import DjangoJSONEncoder
        from django.utils.dateformat import format
        
        payment = get_object_or_404(Payment, id=payment_id)
        billing_history = payment.billing_history
        patient = billing_history.patient
        
        # Préparer les données pour le JSON
        payment_data = {
            'id': payment.id,
            'amount': float(payment.amount),
            'payment_date': payment.payment_date.strftime('%d/%m/%Y'),
            'payment_channel': payment.payment_channel,
            'payment_channel_display': payment.get_payment_channel_display(),
            'payment_mode': payment.payment_mode,
            'payment_mode_display': payment.get_payment_mode_display(),
            'journal': payment.journal,
            'memo': payment.memo,
            'beneficiary_account': payment.beneficiary_account,
            'created_at': payment.created_at.strftime('%d/%m/%Y %H:%M'),
        }
        
        billing_data = {
            'id': billing_history.id,
            'invoice_number': billing_history.invoice_number,
            'total_amount': float(billing_history.total_amount),
            'billing_date': billing_history.billing_date.strftime('%d/%m/%Y'),
            'status': billing_history.status,
            'status_display': billing_history.get_status_display(),
            'notes': billing_history.notes,
        }
        
        patient_data = {
            'id': patient.id,
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'phone': str(patient.phone) if patient.phone else None,
            'email': patient.email,
            'date_of_birth': patient.birth_date.strftime('%d/%m/%Y') if patient.birth_date else None,
            'patient_identifier': patient.patient_identifier,
        }
        
        return JsonResponse({
            'success': True,
            'payment': payment_data,
            'billing_history': billing_data,
            'patient': patient_data,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors du chargement des détails: {str(e)}'
        })


@login_required
def payment_receipt_pdf(request, payment_id):
    """Générer un reçu de paiement en PDF"""
    try:
        from django.http import HttpResponse
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
        from reportlab.lib.units import inch
        from io import BytesIO
        from django.conf import settings
        import os
        
        payment = get_object_or_404(Payment.objects.prefetch_related('partial_payments'), id=payment_id)
        billing_history = payment.billing_history
        patient = billing_history.patient
        
        # Créer le buffer pour le PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
        styles = getSampleStyleSheet()
        
        # Styles personnalisés
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=18,
            textColor=colors.HexColor('#1e90ff'),
            alignment=1,  # Centré
            spaceAfter=20
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e90ff'),
            spaceAfter=10
        )
        
        # Contenu du PDF
        story = []
        
        # Titre
        title = Paragraph("REÇU DE PAIEMENT", title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Informations du paiement
        # Formater le montant payé avec séparateur de milliers
        montant_paye_formate = f"{payment.amount:,.2f}".replace(',', ' ').replace('.', ',')
        
        payment_info = [
            ['N° Facture:', billing_history.invoice_number],
            ['Date de paiement:', payment.payment_date.strftime('%d/%m/%Y')],
            ['Montant payé:', f"{montant_paye_formate} DH"],
            ['Mode de paiement:', payment.get_payment_mode_display()],
        ]
        
        # Canal de paiement : afficher "Multiple" si paiement partiel, sinon le canal normal
        if payment.payment_mode == 'partial':
            payment_info.append(['Canal de paiement:', 'Multiple (voir détails des versements ci-dessous)'])
        else:
            payment_info.append(['Canal de paiement:', payment.get_payment_channel_display()])
        
        if payment.journal:
            payment_info.append(['Journal:', payment.journal])
        if payment.memo:
            payment_info.append(['Mémo:', payment.memo])
        
        payment_table = Table(payment_info, colWidths=[2*inch, 3.5*inch])
        payment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph("Informations du paiement", header_style))
        story.append(payment_table)
        story.append(Spacer(1, 20))
        
        # Si paiement partiel, afficher le détail des versements
        if payment.payment_mode == 'partial':
            partial_payments = payment.partial_payments.all()
            if partial_payments:
                # Titre de la section
                story.append(Paragraph("Détail des versements", header_style))
                
                # En-tête du tableau
                partial_data = [
                    ['N°', 'Canal', 'Montant', 'Date paiement', 'Date échéance']
                ]
                
                # Données des versements
                for partial in partial_payments:
                    # Formater le montant du versement
                    montant_versement = f"{partial.amount:,.2f}".replace(',', ' ').replace('.', ',')
                    partial_data.append([
                        str(partial.payment_number),
                        partial.get_payment_channel_display(),
                        f"{montant_versement} DH",
                        partial.payment_date.strftime('%d/%m/%Y'),
                        partial.due_date.strftime('%d/%m/%Y')
                    ])
                
                # Ligne de total avec formatage
                montant_total_versements = f"{payment.amount:,.2f}".replace(',', ' ').replace('.', ',')
                partial_data.append([
                    '',
                    'TOTAL',
                    f"{montant_total_versements} DH",
                    '',
                    ''
                ])
                
                # Créer le tableau avec largeurs ajustées
                partial_table = Table(partial_data, colWidths=[0.5*inch, 1.3*inch, 1.2*inch, 1*inch, 1*inch])
                partial_table.setStyle(TableStyle([
                    # En-tête
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e90ff')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    # Corps du tableau
                    ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -2), 9),
                    ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # N° centré
                    ('ALIGN', (2, 1), (2, -1), 'RIGHT'),   # Montant aligné à droite
                    ('ALIGN', (3, 1), (4, -1), 'CENTER'),  # Dates centrées
                    # Ligne de total
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f5e9')),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, -1), (-1, -1), 10),
                    ('ALIGN', (1, -1), (1, -1), 'RIGHT'),
                    ('ALIGN', (2, -1), (2, -1), 'RIGHT'),
                    # Bordures
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                ]))
                
                story.append(partial_table)
        story.append(Spacer(1, 20))
        
        # Informations du patient
        patient_info = [
            ['Nom complet:', f"{patient.first_name} {patient.last_name}"],
            ['Identifiant patient:', patient.patient_identifier or '—'],
            ['Téléphone:', str(patient.phone) if patient.phone else '—'],
            ['Email:', patient.email or '—'],
            ['Date de naissance:', patient.birth_date.strftime('%d/%m/%Y') if patient.birth_date else '—'],
        ]
        
        patient_table = Table(patient_info, colWidths=[2*inch, 3.5*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph("Informations du patient", header_style))
        story.append(patient_table)
        story.append(Spacer(1, 20))
        
        # Informations de facturation
        # Formater le montant avec séparateur de milliers
        montant_formate = f"{billing_history.total_amount:,.2f}".replace(',', ' ').replace('.', ',')
        
        billing_info = [
            ['Montant total:', f"{montant_formate} DH"],
            ['Date de facturation:', billing_history.billing_date.strftime('%d/%m/%Y')],
            ['Statut:', billing_history.get_status_display()],
        ]
        
        # Si des notes existent, les ajouter avec un style adapté pour le multiligne
        if billing_history.notes:
            # Créer un Paragraph pour les notes afin de gérer le retour à la ligne automatique
            notes_paragraph = Paragraph(billing_history.notes, styles['Normal'])
            billing_info.append(['Notes:', notes_paragraph])
        
        billing_table = Table(billing_info, colWidths=[2*inch, 3.5*inch])
        billing_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Alignement vertical en haut
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph("Informations de facturation", header_style))
        story.append(billing_table)
        story.append(Spacer(1, 30))
        
        # Signature
        signature_text = Paragraph(
            "Ce reçu certifie que le paiement ci-dessus a été effectué avec succès.<br/><br/>"
            f"Généré le {timezone.now().strftime('%d/%m/%Y à %H:%M')}",
            styles['Normal']
        )
        story.append(signature_text)
        
        # Générer le PDF
        doc.build(story)
        pdf = buffer.getvalue()
        buffer.close()
        
        # Réponse HTTP
        response = HttpResponse(content_type='application/pdf')
        filename = f"recu_paiement_{billing_history.invoice_number}_{payment.payment_date.strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(pdf)
        
        return response
        
    except Exception as e:
        from django.http import JsonResponse
        return JsonResponse({'error': f'Erreur lors de la génération du reçu: {str(e)}'}, status=500)


@login_required
def patient_settings(request):
    """Vue pour la configuration des paramètres du module patient"""
    from .models import ActeTherapeutique, DocumentType, PatientSource
    
    tab = request.GET.get('tab', 'actes')
    
    if request.method == 'POST':
        # Gestion des actes thérapeutiques
        if 'ajouter_acte' in request.POST:
            libelle = request.POST.get('libelle')
            description = request.POST.get('description')
            price = request.POST.get('price')
            duration = request.POST.get('duration')
            is_active = request.POST.get('is_active', 'True') == 'True'
            
            if libelle and price:
                try:
                    ActeTherapeutique.objects.create(
                        libelle=libelle,
                        description=description,
                        price=price,
                        duration=duration if duration else None,
                        is_active=is_active
                    )
                    messages.success(request, f'Acte {libelle} ajouté avec succès!')
                except Exception as e:
                    messages.error(request, f'Erreur lors de l\'ajout de l\'acte: {str(e)}')
            else:
                messages.error(request, 'Tous les champs obligatoires doivent être remplis.')
            
            return redirect('patient:patient_settings')
        
        elif 'modifier_acte' in request.POST:
            acte_id = request.POST.get('acte_id')
            acte = get_object_or_404(ActeTherapeutique, id=acte_id)
            
            acte.libelle = request.POST.get('libelle')
            acte.description = request.POST.get('description')
            acte.price = request.POST.get('price')
            duration = request.POST.get('duration')
            acte.duration = duration if duration else None
            acte.is_active = request.POST.get('is_active', 'True') == 'True'
            acte.save()
            
            messages.success(request, f'Acte {acte.libelle} modifié avec succès!')
            return redirect('patient:patient_settings')
        
        elif 'supprimer_acte' in request.POST:
            acte_id = request.POST.get('acte_id')
            acte = get_object_or_404(ActeTherapeutique, id=acte_id)
            libelle = acte.libelle
            acte.delete()
            
            messages.success(request, f'Acte {libelle} supprimé avec succès!')
            return redirect('patient:patient_settings')
        
        # Gestion des types de documents
        elif 'ajouter_document_type' in request.POST:
            name = request.POST.get('name')
            code = request.POST.get('code')
            description = request.POST.get('description')
            is_active = request.POST.get('is_active', 'True') == 'True'
            
            if name and code:
                try:
                    DocumentType.objects.create(
                        name=name,
                        code=code,
                        description=description,
                        is_active=is_active
                    )
                    messages.success(request, f'Type de document {name} ajouté avec succès!')
                except Exception as e:
                    messages.error(request, f'Erreur lors de l\'ajout du type de document: {str(e)}')
            else:
                messages.error(request, 'Tous les champs obligatoires doivent être remplis.')
            
            return redirect('patient:patient_settings')
        
        elif 'modifier_document_type' in request.POST:
            document_type_id = request.POST.get('document_type_id')
            document_type = get_object_or_404(DocumentType, id=document_type_id)
            
            document_type.name = request.POST.get('name')
            document_type.code = request.POST.get('code')
            document_type.description = request.POST.get('description')
            document_type.is_active = request.POST.get('is_active', 'True') == 'True'
            document_type.save()
            
            messages.success(request, f'Type de document {document_type.name} modifié avec succès!')
            return redirect('patient:patient_settings')
        
        elif 'supprimer_document_type' in request.POST:
            document_type_id = request.POST.get('document_type_id')
            document_type = get_object_or_404(DocumentType, id=document_type_id)
            name = document_type.name
            document_type.delete()
            
            messages.success(request, f'Type de document {name} supprimé avec succès!')
            return redirect('patient:patient_settings')
        
        # Gestion des sources de patients
        elif 'ajouter_source' in request.POST:
            name = request.POST.get('name')
            code = request.POST.get('code')
            description = request.POST.get('description')
            color = request.POST.get('color', '#007bff')
            icon = request.POST.get('icon')
            is_active = request.POST.get('is_active', 'True') == 'True'
            
            if name and code:
                try:
                    PatientSource.objects.create(
                        name=name,
                        code=code,
                        description=description,
                        color=color,
                        icon=icon,
                        is_active=is_active
                    )
                    messages.success(request, f'Source {name} ajoutée avec succès!')
                except Exception as e:
                    messages.error(request, f'Erreur lors de l\'ajout de la source: {str(e)}')
            else:
                messages.error(request, 'Tous les champs obligatoires doivent être remplis.')
            
            return redirect('patient:patient_settings')
        
        elif 'modifier_source' in request.POST:
            source_id = request.POST.get('source_id')
            source = get_object_or_404(PatientSource, id=source_id)
            
            source.name = request.POST.get('name')
            source.code = request.POST.get('code')
            source.description = request.POST.get('description')
            source.color = request.POST.get('color', '#007bff')
            source.icon = request.POST.get('icon')
            source.is_active = request.POST.get('is_active', 'True') == 'True'
            source.save()
            
            messages.success(request, f'Source {source.name} modifiée avec succès!')
            return redirect('patient:patient_settings')
        
        elif 'supprimer_source' in request.POST:
            source_id = request.POST.get('source_id')
            source = get_object_or_404(PatientSource, id=source_id)
            name = source.name
            source.delete()
            
            messages.success(request, f'Source {name} supprimée avec succès!')
            return redirect('patient:patient_settings')
    
    # Récupération des données
    actes = ActeTherapeutique.objects.all().order_by('libelle')
    document_types = DocumentType.objects.all().order_by('name')
    sources = PatientSource.objects.all().order_by('name')
    
    # Pagination des actes
    actes_paginator = Paginator(actes, 10)
    actes_page = request.GET.get('actes_page', 1)
    actes_page_obj = actes_paginator.get_page(actes_page)
    
    # Pagination des types de documents
    document_types_paginator = Paginator(document_types, 10)
    document_types_page = request.GET.get('document_types_page', 1)
    document_types_page_obj = document_types_paginator.get_page(document_types_page)
    
    # Pagination des sources
    sources_paginator = Paginator(sources, 10)
    sources_page = request.GET.get('sources_page', 1)
    sources_page_obj = sources_paginator.get_page(sources_page)
    
    context = {
        'actes': actes_page_obj,
        'document_types': document_types_page_obj,
        'sources': sources_page_obj,
        'actes_paginated': actes_page_obj.has_other_pages(),
        'actes_page_obj': actes_page_obj,
        'document_types_paginated': document_types_page_obj.has_other_pages(),
        'document_types_page_obj': document_types_page_obj,
        'sources_paginated': sources_page_obj.has_other_pages(),
        'sources_page_obj': sources_page_obj,
        'tab': tab,
    }
    
    return render(request, 'patient_settings.html', context)
