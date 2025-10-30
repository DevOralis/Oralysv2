from django.views.generic import  View
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.template.loader import render_to_string
try:
    from weasyprint import HTML
except Exception:
    HTML = None
from apps.home.utils import log_action
from django.forms.models import model_to_dict
from .models import Admission, Room, Bed, Reservation, Companion,room_type,bed_status
from .forms import AdmissionForm, RoomForm, BedForm, ReservationForm, CompanionForm, RoomTypeForm, BedStatusForm
from django.db.models import Count, Q, Max
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from apps.patient.models import Patient,Consultation
from django.core.paginator import Paginator
import re
import logging

logger = logging.getLogger(__name__)

def generate_bed_id():
    """Générer un bed_id au format LIT-XXX (auto-incrémenté)."""
    last_bed = Bed.objects.order_by('bed_id').last()
    if not last_bed or not last_bed.bed_id:
        return 'LIT-001'
    
    last_id = last_bed.bed_id
    match = re.match(r'^LIT-(\d+)$', last_id)
    if match:
        number = int(match.group(1)) + 1
    else:
        beds = Bed.objects.filter(bed_id__startswith='LIT-').order_by('bed_id')
        max_number = 0
        for bed in beds:
            match = re.match(r'^LIT-(\d+)$', bed.bed_id)
            if match:
                max_number = max(max_number, int(match.group(1)))
        number = max_number + 1
    
    return f'LIT-{number:03d}'

def bed_list(request):
    """Lister les lits avec pagination et filtres."""
    beds = Bed.objects.all().order_by('bed_number')
    bed_statuses = bed_status.BedStatus.objects.all()
    
    status_filter = request.GET.get('bed_status', '')
    search_query = request.GET.get('q', '')
    
    if status_filter:
        beds = beds.filter(bed_status__id=status_filter)
    if search_query:
        beds = beds.filter(bed_number__icontains=search_query) | \
               beds.filter(room__room_name__icontains=search_query)
    
    paginator = Paginator(beds, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'beds.html', {
        'beds': page_obj,
        'bed_statuses': bed_statuses,
        'form': BedForm(),
        'page_obj': page_obj,
        'rooms': Room.objects.all(),
    })

def bed_create(request):
    """Créer un nouveau lit."""
    if request.method == 'POST':
        form = BedForm(request.POST)
        if form.is_valid():
            # Vérifier la capacité de la chambre avant création
            room = form.cleaned_data.get('room')
            if room:
                existing_beds_count = Bed.objects.filter(room=room).count()
                if existing_beds_count >= room.capacity:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'status': 'error', 
                            'message': 'Chambre capacité maximale atteinte',
                            'alert_type': 'capacity_error'
                        }, status=400)
                    messages.error(request, 'Chambre capacité maximale atteinte')
                    return redirect('bed_list')
            
            bed = form.save(commit=False)
            if not bed.bed_id:
                bed.bed_id = generate_bed_id()
            try:
                bed.save()
                log_action(request.user, bed, 'creation')  # Moved after save
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success', 'message': 'Lit créé avec succès.'})
                messages.success(request, 'Lit créé avec succès.')
                return redirect('bed_list')
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': str(e), 'errors': form.errors}, status=400)
                messages.error(request, f'Erreur lors de la création : {str(e)}')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Veuillez corriger les erreurs dans le formulaire.', 'errors': form.errors}, status=400)
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = BedForm()
    
    return render(request, 'beds.html', {
        'form': form,
        'beds': Bed.objects.all().order_by('bed_number'),
        'bed_statuses': bed_status.BedStatus.objects.all(),
        'rooms': Room.objects.all(),
    })

def bed_update(request, bed_id):
    """Mettre à jour un lit existant."""
    bed = get_object_or_404(Bed, bed_id=bed_id)
    if request.method == 'POST':
        form = BedForm(request.POST, instance=bed)
        if form.is_valid():
            try:
                bed = form.save()  # Store the saved instance
                log_action(request.user, bed, 'modification')
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success', 'message': 'Lit mis à jour avec succès.'})
                messages.success(request, 'Lit mis à jour avec succès.')
                return redirect('bed_list')
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': str(e), 'errors': form.errors}, status=400)
                messages.error(request, f'Erreur lors de la mise à jour : {str(e)}')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Veuillez corriger les erreurs dans le formulaire.', 'errors': form.errors}, status=400)
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = BedForm(instance=bed)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form_data = {
                'bed_number': form['bed_number'].value(),
                'room': form['room'].value(),
                'bed_status': form['bed_status'].value(),
            }
            return JsonResponse({'status': 'success', 'form': form_data})
    
    return render(request, 'beds.html', {'form': form, 'bed': bed})

def bed_delete(request, bed_id):
    """Supprimer un lit."""
    bed = get_object_or_404(Bed, bed_id=bed_id)
    if request.method == 'POST':
        try:
            log_action(request.user, bed, 'suppression')  # Log before deletion
            bed.delete()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Lit supprimé avec succès.'})
            messages.success(request, 'Lit supprimé avec succès.')
            return redirect('bed_list')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            messages.error(request, f'Erreur lors de la suppression : {str(e)}')
    else:
        return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)

def bed_release(request, bed_id):
    """Libérer un lit (statut à Disponible)."""
    bed = get_object_or_404(Bed, bed_id=bed_id)
    if request.method == 'POST':
        try:
            available_status = bed_status.BedStatus.objects.get(name='available')
            bed.bed_status = available_status
            bed.save()
            log_action(request.user, bed, 'modification')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Lit libéré avec succès.'})
            messages.success(request, 'Lit libéré avec succès.')
            return redirect('bed_list')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            messages.error(request, f'Erreur lors de la libération : {str(e)}')
            return redirect('bed_list')
    else:
        return render(request, 'beds.html', {
            'bed': bed,
            'beds': Bed.objects.all().order_by('bed_number'),
            'bed_statuses': bed_status.BedStatus.objects.all(),
            'rooms': Room.objects.all(),
            'form': BedForm(),
        })

def generate_bed_id_view(request):
    """Générer un nouvel identifiant de lit pour le formulaire."""
    try:
        generated_id = generate_bed_id()
        return JsonResponse({'status': 'success', 'generated_id': generated_id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def patient_hosting_summary(request):
    """Résumé d'hébergement pour un patient avec calculs automatiques."""
    from apps.patient.models import Patient
    from apps.patient.models.acte import Acte
    from decimal import Decimal
    
    patients = Patient.objects.all().order_by('last_name', 'first_name')
    selected_patient_id = request.GET.get('patient_id')
    selected_patient = None
    admissions = []
    companions = []
    total_cout = None
    
    if selected_patient_id:
        try:
            selected_patient = get_object_or_404(Patient, id=selected_patient_id)
            
            # Récupérer les admissions avec calculs
            admissions_qs = Admission.objects.filter(patient=selected_patient).order_by('-admission_date')
            
            total_hebergement = Decimal('0')
            total_accompagnant = Decimal('0')
            
            # Traitement des admissions
            for admission in admissions_qs:
                if admission.discharge_date:
                    # Calculer nombre de jours
                    nb_jours = (admission.discharge_date - admission.admission_date).days
                    if nb_jours <= 0:
                        nb_jours = 1
                    admission.nb_jours = nb_jours
                    
                    # Déterminer type de chambre et tarif
                    room_type_mapping = {
                        'vip': 'VIP',
                        'single': 'Simple',
                        'double': 'Double'
                    }
                    
                    if hasattr(admission.room, 'room_type') and hasattr(admission.room.room_type, 'type_name'):
                        room_type_name = admission.room.room_type.type_name.lower()
                        acte_name = room_type_mapping.get(room_type_name, 'Simple')
                        admission.room_type_display = acte_name
                    else:
                        room_type_str = admission.room_type.lower() if admission.room_type else 'simple'
                        acte_name = room_type_mapping.get(room_type_str, 'Simple')
                        admission.room_type_display = acte_name
                    
                    try:
                        acte_hebergement = Acte.objects.get(libelle__icontains=acte_name)
                        admission.acte_hebergement = acte_hebergement
                        admission.cout_total = acte_hebergement.price * nb_jours
                        total_hebergement += admission.cout_total
                    except Acte.DoesNotExist:
                        admission.acte_hebergement = None
                        admission.cout_total = Decimal('0')
                else:
                    admission.nb_jours = None
                    admission.acte_hebergement = None
                    admission.cout_total = Decimal('0')
            
            admissions = list(admissions_qs)
            
            # Traitement des accompagnants
            companions_qs = Companion.objects.filter(patient=selected_patient).order_by('-start_date')
            
            for companion in companions_qs:
                if companion.accommodation_start_date and companion.accommodation_end_date:
                    # Calculer nombre de jours d'accompagnement
                    nb_jours_acc = (companion.accommodation_end_date - companion.accommodation_start_date).days
                    if nb_jours_acc <= 0:
                        nb_jours_acc = 1
                    companion.nb_jours_acc = nb_jours_acc
                    
                    try:
                        acte_accompagnant = Acte.objects.get(libelle__icontains='Accompagnant')
                        companion.acte_accompagnant = acte_accompagnant
                        companion.cout_total = acte_accompagnant.price * nb_jours_acc
                        total_accompagnant += companion.cout_total
                    except Acte.DoesNotExist:
                        companion.acte_accompagnant = None
                        companion.cout_total = Decimal('0')
                else:
                    companion.nb_jours_acc = None
                    companion.acte_accompagnant = None
                    companion.cout_total = Decimal('0')
            
            companions = list(companions_qs)
            
            # Calcul total
            if total_hebergement > 0 or total_accompagnant > 0:
                total_cout = {
                    'hebergement': total_hebergement,
                    'accompagnant': total_accompagnant,
                    'total': total_hebergement + total_accompagnant
                }
            
        except Patient.DoesNotExist:
            selected_patient = None
    
    context = {
        'patients': patients,
        'selected_patient_id': selected_patient_id,
        'selected_patient': selected_patient,
        'admissions': admissions,
        'companions': companions,
        'total_cout': total_cout,
    }
    
    return render(request, 'patient_hosting_summary.html', context)

def create_hosting_invoice(request, patient_id):
    """Créer une facture d'hébergement automatiquement et rediriger vers l'app patient."""
    from apps.patient.models import Patient, Invoice, Consultation
    from apps.patient.models.acte import Acte
    from django.contrib import messages
    from decimal import Decimal
    
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        
        # Vérifier s'il y a des données d'hébergement
        admissions = Admission.objects.filter(patient=patient)
        companions = Companion.objects.filter(patient=patient)
        
        if not admissions.exists() and not companions.exists():
            messages.error(request, 'Aucune donnée d\'hébergement trouvée pour ce patient.')
            return redirect('hosting:patient_hosting_summary')
        
        # Créer une consultation factice pour l'hébergement si aucune consultation facturée n'existe
        consultation = Consultation.objects.filter(patient=patient, is_invoiced=True).first()
        if not consultation:
            # Créer une consultation d'hébergement
            consultation = Consultation.objects.create(
                patient=patient,
                medecin=None,
                commentaires='Consultation automatique pour hébergement',
                traitement='Hébergement et soins associés',
                hospitalisation=True,
                is_invoiced=True
            )
        
        # Créer la facture
        invoice = Invoice.objects.create(
            patient=patient,
            consultation=consultation,
            invoice_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=30)
        )
        
        messages.success(request, f'Facture d\'hébergement créée avec succès (N° {invoice.id})')
        
        # Rediriger vers la page de facturation dans l'app patient
        return redirect('patient:invoice_pdf', invoice_id=invoice.id)
        
    except Exception as e:
        messages.error(request, f'Erreur lors de la création de la facture: {str(e)}')
        return redirect('hosting:patient_hosting_summary')

def bed_detail(request, bed_id):
    """Récupérer les détails d'un lit pour le formulaire AJAX."""
    try:
        bed = get_object_or_404(Bed, bed_id=bed_id)
        logger.info(f"Récupération des détails du lit pour bed_id: {bed_id}")
        return JsonResponse({
            'status': 'success',
            'bed': {
                'bed_id': bed.bed_id,
                'bed_number': bed.bed_number,
                'room': str(bed.room.room_id),
                'bed_status': str(bed.bed_status.id),
            }
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des détails pour bed_id {bed_id}: {str(e)}")
        return JsonResponse({'status': 'error', 'message': f'Erreur lors de la récupération des données : {str(e)}'}, status=400)

def bed_pdf(request, bed_id):
    """Générer un PDF pour un lit."""
    bed = get_object_or_404(Bed, bed_id=bed_id)
    
    html_string = render_to_string('bed_pdf.html', {'bed': bed})
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="lit_{bed.bed_id}.pdf"'
    HTML(string=html_string).write_pdf(response)
    log_action(request.user, bed, 'impression')
    
    return response


def reservation_list(request):
    """Display the list of reservations with filtering and pagination."""
    status = request.GET.get('status')
    reservations = Reservation.objects.all()
    
    VALID_STATUSES = [choice[0] for choice in Reservation.RESERVATION_STATUS]
    
    if status and status in VALID_STATUSES:
        reservations = reservations.filter(reservation_status=status)
    elif status:
        messages.warning(request, f"Statut '{status}' non valide. Affichage de toutes les réservations.")
    
    reservation_statuses = Reservation.RESERVATION_STATUS
    paginator = Paginator(reservations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    form = ReservationForm()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        reservations_data = [
            {
                'reservation_id': reservation.reservation_id,
                'patient': str(reservation.patient),
                'room': reservation.room.room_name if reservation.room else 'Non assignée',
                'bed': reservation.bed.bed_number if reservation.bed else 'Non assigné',
                'start_date': reservation.start_date.isoformat() if reservation.start_date else '',
                'end_date': reservation.end_date.isoformat() if reservation.end_date else '',
                'reservation_status': reservation.get_reservation_status_display()
            } for reservation in page_obj
        ]
        return JsonResponse({
            'status': 'success',
            'reservations': reservations_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'page_number': page_obj.number
        })
    
    context = {
        'reservations': page_obj,
        'reservation_statuses': reservation_statuses,
        'form': form,
        'page_obj': page_obj
    }
    return render(request, 'reservations.html', context)

def reservation_create(request):
    """Create a new reservation."""
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            try:
                reservation = form.save()
                log_action(request.user, reservation, 'creation')
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success', 'message': 'Réservation créée avec succès.'})
                messages.success(request, 'Réservation créée avec succès.')
                return redirect('reservation_list')
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': str(e), 'errors': form.errors}, status=400)
                messages.error(request, f'Erreur lors de la création : {str(e)}')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Veuillez corriger les erreurs dans le formulaire.', 'errors': form.errors}, status=400)
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = ReservationForm()
    
    return render(request, 'reservations.html', {'form': form})

def reservation_update(request, reservation_id):
    """Update an existing reservation."""
    reservation = get_object_or_404(Reservation, reservation_id=reservation_id)
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            try:
                reservation = form.save()
                log_action(request.user, reservation, 'modification')
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success', 'message': 'Réservation mise à jour avec succès.'})
                messages.success(request, 'Réservation mise à jour avec succès.')
                return redirect('reservation_list')
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': str(e), 'errors': form.errors}, status=400)
                messages.error(request, f'Erreur lors de la mise à jour : {str(e)}')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Veuillez corriger les erreurs dans le formulaire.', 'errors': form.errors}, status=400)
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = ReservationForm(instance=reservation)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form_data = {
                'patient': form['patient'].value() or '',
                'room': form['room'].value() or '',
                'bed': form['bed'].value() or '',
                'start_date': form['start_date'].value() or '',
                'end_date': form['end_date'].value() or '',
                'reservation_status': form['reservation_status'].value() or ''
            }
            return JsonResponse({'status': 'success', 'form': form_data})
    
    return render(request, 'reservations.html', {'form': form, 'reservation': reservation})

def reservation_delete(request, reservation_id):
    """Delete a reservation."""
    reservation = get_object_or_404(Reservation, reservation_id=reservation_id)
    if request.method == 'POST':
        try:
            log_action(request.user, reservation, 'suppression')  # Log before deletion
            reservation.delete()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Réservation supprimée avec succès.'})
            messages.success(request, 'Réservation supprimée avec succès.')
            return redirect('reservation_list')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            messages.error(request, f'Erreur lors de la suppression : {str(e)}')
    return redirect('reservation_list')

def reservation_details(request, reservation_id):
    """Display reservation details."""
    reservation = get_object_or_404(Reservation, reservation_id=reservation_id)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'reservation': {
                'reservation_id': reservation.reservation_id,
                'patient': str(reservation.patient),
                'room': reservation.room.room_name if reservation.room else 'Non assignée',
                'bed': reservation.bed.bed_number if reservation.bed else 'Non assigné',
                'start_date': reservation.start_date.isoformat() if reservation.start_date else '',
                'end_date': reservation.end_date.isoformat() if reservation.end_date else '',
                'reservation_status': reservation.get_reservation_status_display()
            }
        })
    return render(request, 'reservations.html', {'reservation': reservation})

def confirm_reservation(request, reservation_id):
    """Confirm a pending reservation."""
    reservation = get_object_or_404(Reservation, reservation_id=reservation_id)
    if request.method == 'POST':
        if reservation.reservation_status != 'pending':
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Seules les réservations en attente peuvent être confirmées.'}, status=400)
            messages.error(request, 'Seules les réservations en attente peuvent être confirmées.')
            return redirect('reservation_list')
        
        try:
            reservation.reservation_status = 'confirmed'
            reservation.save()
            log_action(request.user, reservation, 'confirmation')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Réservation confirmée avec succès.'})
            messages.success(request, 'Réservation confirmée avec succès.')
            return redirect('reservation_list')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            messages.error(request, f'Erreur lors de la confirmation : {str(e)}')
    return redirect('reservation_list')

def reservation_pdf(request, reservation_id):
    """Générer un PDF pour une réservation spécifique."""
    reservation = get_object_or_404(Reservation, reservation_id=reservation_id)
    
    html_string = render_to_string('reservation_pdf.html', {
        'reservation': reservation
    })
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="reservation_{reservation.reservation_id}.pdf"'
    HTML(string=html_string).write_pdf(response)
    log_action(request.user, reservation, 'impression')
    return response

def admission_list(request):
    """Liste des admissions avec pagination et filtres."""
    admissions = Admission.objects.all().order_by('-admission_date')
    patients = Admission._meta.get_field('patient').related_model.objects.all()
    consultations = Admission._meta.get_field('consultation').related_model.objects.all()
    room_types = room_type.RoomType.objects.filter(is_active=True)

    rooms = Room.objects.all()
    beds = Bed.objects.all()
    assignment_modes = Admission.ASSIGNMENT_MODE
    discharge_reasons = Admission.DISCHARGE_REASON

    discharge_reason = request.GET.get('discharge_reason', '')
    search_query = request.GET.get('q', '')
    if discharge_reason:
        admissions = admissions.filter(discharge_reason=discharge_reason)
    if search_query:
        admissions = admissions.filter(patient__name__icontains=search_query)

    paginator = Paginator(admissions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form = AdmissionForm()

    context = {
        'admissions': page_obj,
        'patients': patients,
        'consultations': consultations,
        'rooms': rooms,
        'beds': beds,
        'assignment_modes': assignment_modes,
        'discharge_reasons': discharge_reasons,
        'form': form,
        'page_obj': page_obj,
        'room_types': room_types,
    }
    return render(request, 'admissions.html', context)

def admission_create(request):
    """Créer une nouvelle admission."""
    if request.method == 'POST':
        form = AdmissionForm(request.POST)
        if form.is_valid():
            try:
                admission = form.save()
                log_action(request.user, admission, 'creation')
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success', 'message': 'Admission créée avec succès.'})
                messages.success(request, "Admission créée avec succès.")
                return redirect('admission_list')
            except Exception as e:
                print(f"Error creating admission: {str(e)}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': str(e), 'errors': form.errors}, status=400)
                messages.error(request, f"Erreur lors de la création de l'admission: {str(e)}")
        else:
            print(f"Form errors: {form.errors}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Erreur dans le formulaire.', 'errors': form.errors}, status=400)
            messages.error(request, "Erreur lors de la création de l'admission.")
    else:
        form = AdmissionForm()
    
    patients = Patient.objects.all()
    consultations = Consultation.objects.all()
    rooms = Room.objects.all()
    beds = Bed.objects.all()
    assignment_modes = Admission.ASSIGNMENT_MODE
    discharge_reasons = Admission.DISCHARGE_REASON
    room_types = room_type.RoomType.objects.filter(is_active=True)

    context = {
        'form': form,
        'patients': patients,
        'consultations': consultations,
        'rooms': rooms,
        'beds': beds,
        'assignment_modes': assignment_modes,
        'discharge_reasons': discharge_reasons,
        'room_types': room_types,
    }
    return render(request, 'admissions.html', context)

def admission_update(request, admission_id):
    """Modifier une admission existante."""
    admission = get_object_or_404(Admission, pk=admission_id)
    
    if request.method == 'POST':
        form = AdmissionForm(request.POST, instance=admission)
        if form.is_valid():
            try:
                updated_admission = form.save()
                log_action(request.user, updated_admission, 'modification')
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success', 
                        'message': 'Admission modifiée avec succès.',
                        'redirect': reverse('admission_list')
                    })
                
                messages.success(request, "Admission modifiée avec succès.")
                return redirect('admission_list')
                
            except Exception as e:
                logger.error(f"Erreur lors de la modification de l'admission {admission_id}: {str(e)}")
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error', 
                        'message': f'Erreur lors de la modification: {str(e)}',
                        'errors': form.errors
                    }, status=400)
                
                messages.error(request, f"Erreur lors de la modification de l'admission: {str(e)}")
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Erreur de validation du formulaire.',
                    'errors': form.errors
                }, status=400)
            
            messages.error(request, "Erreur lors de la modification de l'admission.")
    else:
        form = AdmissionForm(instance=admission)
    
    patients = Patient.objects.all()
    consultations = Consultation.objects.all()
    rooms = Room.objects.all()
    beds = Bed.objects.all()
    assignment_modes = Admission.ASSIGNMENT_MODE
    discharge_reasons = Admission.DISCHARGE_REASON
    room_types = room_type.RoomType.objects.filter(is_active=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form_data = {
            'patient': form['patient'].value() or '',
            'consultation': form['consultation'].value() or '',
            'assignment_mode': form['assignment_mode'].value() or '',
            'room': form['room'].value() or '',
            'bed': form['bed'].value() or '',
            'room_type': form['room_type'].value() or '',
            'admission_date': form['admission_date'].value().strftime('%Y-%m-%d') if form['admission_date'].value() else '',
            'discharge_date': form['discharge_date'].value().strftime('%Y-%m-%d') if form['discharge_date'].value() else '',
            'discharge_reason': form['discharge_reason'].value() or '',
            'notes': form['notes'].value() or ''
        }
        return JsonResponse({
            'status': 'success',
            'form': form_data,
            'admission': model_to_dict(admission)
        })
    
    context = {
        'form': form,
        'admission': admission,
        'patients': patients,
        'consultations': consultations,
        'rooms': rooms,
        'beds': beds,
        'assignment_modes': assignment_modes,
        'discharge_reasons': discharge_reasons,
        'room_types': room_types,
        'is_edit_mode': True
    }
    
    return render(request, 'admissions.html', context)

def admission_delete(request, admission_id):
    """Supprimer une admission."""
    admission = get_object_or_404(Admission, pk=admission_id)
    if request.method == 'POST':
        log_action(request.user, admission, 'suppression')  # Log before deletion
        admission.delete()
        messages.success(request, "Admission supprimée avec succès.")
        return redirect('admission_list')
    return render(request, 'admissions.html', {'admission': admission})

def admission_detail(request, admission_id):
    """Afficher les détails d'une admission."""
    admission = get_object_or_404(Admission, pk=admission_id)
    return render(request, 'admissions.html', {'admission': admission})

def admission_pdf(request, admission_id):
    """Générer un PDF pour une admission spécifique."""
    admission = get_object_or_404(Admission, admission_id=admission_id)
    
    html_string = render_to_string('admission_pdf.html', {
        'admission': admission
    })
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="admission_{admission.admission_id}.pdf"'
    HTML(string=html_string).write_pdf(response)
    log_action(request.user, admission, 'impression')
    return response
class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        # Statistiques de base
        total_rooms = Room.objects.count()  # Compte basé sur room_id ou tout autre champ unique
        occupied_rooms = Room.objects.filter(admissions__discharge_date__isnull=True).distinct().count()
        occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
        admissions = Admission.objects.all().order_by('-admission_date')[:10]  # 10 dernières admissions
        reservations = Reservation.objects.all().order_by('-start_date')[:10]  # 10 dernières réservations
        room_types = Room.ROOM_TYPE  # Obtenir les choix de type de chambre

        # Données pour le graphique "Évolution des admissions"
        end_date = timezone.now()
        periods = {
            '7': end_date - timedelta(days=7),
            '30': end_date - timedelta(days=30),
            '90': end_date - timedelta(days=90)
        }
        admission_counts = {}
        for period, start_date in periods.items():
            count = Admission.objects.filter(admission_date__gte=start_date, admission_date__lte=end_date).count()
            admission_counts[period] = count

        # Données pour le graphique "Répartition par type de chambre"
        room_type_counts = Room.objects.values('room_type').annotate(count=Count('room_id')).order_by()  # Utilise room_id

        context = {
            'total_rooms': total_rooms,
            'occupied_rooms': occupied_rooms,
            'occupancy_rate': occupancy_rate,
            'admissions': admissions,
            'reservations': reservations,
            'room_types': room_types,
            'admission_counts': admission_counts,  # Données pour le graphique ligne
            'room_type_counts': room_type_counts,  # Données pour le graphique pie
        }
        return render(request, 'hosting_dashboard.html', context)
# Chart Data View for dynamic updates
class ChartDataView(LoginRequiredMixin, View):
    def get(self, request):
        period = request.GET.get('period', '30')  # Default to 30 days
        end_date = timezone.now()
        start_date = end_date - timedelta(days=int(period))
        count = Admission.objects.filter(admission_date__gte=start_date, admission_date__lte=end_date).count()

        # Return counts for all periods for consistency
        periods = {
            '7': end_date - timedelta(days=7),
            '30': end_date - timedelta(days=30),
            '90': end_date - timedelta(days=90)
        }
        data = {
            'count_7': Admission.objects.filter(admission_date__gte=periods['7'], admission_date__lte=end_date).count(),
            'count_30': Admission.objects.filter(admission_date__gte=periods['30'], admission_date__lte=end_date).count(),
            'count_90': Admission.objects.filter(admission_date__gte=periods['90'], admission_date__lte=end_date).count(),
        }
        return JsonResponse(data)

def generate_room_id():
    """Générer un room_id au format CH-XXX (auto-incrémenté)."""
    last_room = Room.objects.order_by('room_id').last()
    if not last_room or not last_room.room_id:
        return 'CH-001'
    
    last_id = last_room.room_id
    # Vérifier si le format est CH-XXX
    match = re.match(r'^CH-(\d+)$', last_id)
    if match:
        number = int(match.group(1)) + 1
    else:
        # Si le format est incorrect, trouver le dernier numéro parmi tous les room_id
        rooms = Room.objects.filter(room_id__startswith='CH-').order_by('room_id')
        max_number = 0
        for room in rooms:
            match = re.match(r'^CH-(\d+)$', room.room_id)
            if match:
                max_number = max(max_number, int(match.group(1)))
        number = max_number + 1
    
    return f'CH-{number:03d}'

def room_list(request):
    rooms = Room.objects.all().order_by('room_name')
    room_types = room_type.RoomType.objects.all()

    room_type_filter = request.GET.get('room_type', '')
    search_query = request.GET.get('q', '')
    
    if room_type_filter:
        rooms = rooms.filter(room_type__id=room_type_filter)
    if search_query:
        rooms = rooms.filter(room_name__icontains=search_query) | \
                rooms.filter(room_id__icontains=search_query)
    
    paginator = Paginator(rooms, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'rooms.html', {
        'rooms': page_obj,
        'room_types': room_types,
        'form': RoomForm(),
        'page_obj': page_obj,
    })

def room_create(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            if not room.room_id:
                room.room_id = generate_room_id()
            try:
                room.save()
                log_action(request.user, room, 'creation')
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success', 'message': 'Chambre créée avec succès.'})
                messages.success(request, 'Chambre créée avec succès.')
                return redirect('room_list')
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': str(e), 'errors': form.errors}, status=400)
                messages.error(request, f'Erreur lors de la création : {str(e)}')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Veuillez corriger les erreurs dans le formulaire.', 'errors': form.errors}, status=400)
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = RoomForm()
    
    return render(request, 'rooms.html', {
        'form': form,
        'rooms': Room.objects.all().order_by('room_name'),
        'room_types': room_type.RoomType.objects.all(),
    })

def room_update(request, room_id):
    room = get_object_or_404(Room, room_id=room_id)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            try:
                room = form.save()
                log_action(request.user, room, 'modification')
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success', 'message': 'Chambre mise à jour avec succès.'})
                messages.success(request, 'Chambre mise à jour avec succès.')
                return redirect('room_list')
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': str(e), 'errors': form.errors}, status=400)
                messages.error(request, f'Erreur lors de la mise à jour : {str(e)}')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Veuillez corriger les erreurs dans le formulaire.', 'errors': form.errors}, status=400)
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = RoomForm(instance=room)
    
    return render(request, 'rooms.html', {
        'form': form,
        'room': room,
        'rooms': Room.objects.all().order_by('room_name'),
        'room_types': room_type.RoomType.objects.all(),
    })

def room_delete(request, room_id):
    room = get_object_or_404(Room, room_id=room_id)
    if request.method == 'POST':
        try:
            log_action(request.user, room, 'suppression')  # Log before deletion
            room.delete()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Chambre supprimée avec succès.'})
            messages.success(request, 'Chambre supprimée avec succès.')
            return redirect('room_list')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            messages.error(request, f'Erreur lors de la suppression : {str(e)}')
    else:
        return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)

def room_release(request, room_id):
    room = get_object_or_404(Room, room_id=room_id)
    if request.method == 'POST':
        try:
            room.status = 'available'
            room.save()
            log_action(request.user, room, 'modification')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Chambre libérée avec succès.'})
            messages.success(request, 'Chambre libérée avec succès.')
            return redirect('room_list')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            messages.error(request, f'Erreur lors de la libération : {str(e)}')
            return redirect('room_list')
    else:
        return render(request, 'rooms.html', {
            'room': room,
            'rooms': Room.objects.all().order_by('room_name'),
            'room_types': room_type.RoomType.objects.all(),
            'form': RoomForm(),
        })

def generate_room_id_view(request):
    try:
        generated_id = generate_room_id()
        return JsonResponse({'status': 'success', 'generated_id': generated_id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def room_detail(request, room_id):
    try:
        room = get_object_or_404(Room, room_id=room_id)
        logger.info(f"Fetching room details for room_id: {room_id}")
        return JsonResponse({
            'status': 'success',
            'room': {
                'room_id': room.room_id,
                'room_name': room.room_name,
                'room_type': str(room.room_type.id),
                'capacity': room.capacity,
                'status': room.status,
                'description': room.description or '',
            }
        })
    except Exception as e:
        logger.error(f"Error fetching room details for room_id {room_id}: {str(e)}")
        return JsonResponse({'status': 'error', 'message': f'Erreur lors de la récupération des données : {str(e)}'}, status=400) 

def room_pdf(request, room_id):
    """Générer un PDF pour une chambre avec ses réservations."""
    room = get_object_or_404(Room, room_id=room_id)
    reservations = room.reservations.all().select_related('patient', 'bed')
    
    html_string = render_to_string('room_pdf.html', {
        'room': room,
        'reservations': reservations
    })
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="chambre_{room.room_id}.pdf"'
    HTML(string=html_string).write_pdf(response)
    log_action(request.user, room, 'impression')
    return response
    
def companion_list(request):
    """Display the list of companions with filtering and pagination."""
    companions = Companion.objects.select_related('patient', 'room', 'bed').all()

    relationship_filter = request.GET.get('relationship', '')
    search_query = request.GET.get('q', '')

    if relationship_filter:
        companions = companions.filter(relationship=relationship_filter)
    
    if search_query:
        companions = companions.filter(
            Q(companion_name__icontains=search_query) |
            Q(patient__name__icontains=search_query) |
            Q(relationship__icontains=search_query)
        )

    relationships = Companion.objects.values_list('relationship', flat=True).distinct().order_by('relationship')

    paginator = Paginator(companions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    allowed_params = {'relationship', 'page', 'q'}
    unwanted_params = [param for param in request.GET.keys() if param not in allowed_params]
    
    if unwanted_params:
        print(f"Unwanted parameters detected: {unwanted_params}")
        for param in unwanted_params:
            print(f"Parameter '{param}' with value '{request.GET.get(param)}'")
        
        messages.warning(request, f"Paramètres non reconnus ignorés: {', '.join(unwanted_params)}")

    form = CompanionForm()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        companions_data = [
            {
                'companion_id': companion.companion_id,
                'companion_name': companion.companion_name,
                'patient': str(companion.patient),
                'relationship': companion.relationship,
                'start_date': companion.start_date.isoformat() if companion.start_date else '',
                'end_date': companion.end_date.isoformat() if companion.end_date else 'En cours',
                'room': companion.room.room_name if companion.room else 'Non assigné',
                'bed': companion.bed.bed_number if companion.bed else 'Non assigné'
            } for companion in page_obj
        ]
        return JsonResponse({
            'status': 'success',
            'companions': companions_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'page_number': page_obj.number
        })
    
    context = {
        'companions': page_obj,
        'relationships': relationships,
        'form': form,
        'page_obj': page_obj,
        'current_relationship': relationship_filter,
        'search_query': search_query
    }
    return render(request, 'companions.html', context)

def companion_create(request):
    """Create a new companion."""
    if request.method == 'POST':
        form = CompanionForm(request.POST)
        if form.is_valid():
            try:
                companion = form.save()
                log_action(request.user, companion, 'creation')
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success', 'message': 'Accompagnant créé avec succès.'})
                messages.success(request, 'Accompagnant créé avec succès.')
                return redirect('companion_list')
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': str(e), 'errors': form.errors}, status=400)
                messages.error(request, f'Erreur lors de la création : {str(e)}')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Veuillez corriger les erreurs dans le formulaire.', 'errors': form.errors}, status=400)
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = CompanionForm()
    
    return render(request, 'companions.html', {'form': form})

def companion_update(request, companion_id):
    """Update an existing companion."""
    companion = get_object_or_404(Companion, companion_id=companion_id)
    if request.method == 'POST':
        form = CompanionForm(request.POST, instance=companion)
        if form.is_valid():
            try:
                companion = form.save()
                log_action(request.user, companion, 'modification')
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success', 'message': 'Accompagnant mis à jour avec succès.'})
                messages.success(request, 'Accompagnant mis à jour avec succès.')
                return redirect('companion_list')
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': str(e), 'errors': form.errors}, status=400)
                messages.error(request, f'Erreur lors de la mise à jour : {str(e)}')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Veuillez corriger les erreurs dans le formulaire.', 'errors': form.errors}, status=400)
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = CompanionForm(instance=companion)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form_data = {
                'companion_name': form['companion_name'].value() or '',
                'patient': form['patient'].value() or '',
                'relationship': form['relationship'].value() or '',
                'start_date': form['start_date'].value() or '',
                'end_date': form['end_date'].value() or '',
                'room': form['room'].value() or '',
                'bed': form['bed'].value() or '',
                'accommodation_start_date': form['accommodation_start_date'].value() or '',
                'accommodation_end_date': form['accommodation_end_date'].value() or '',
                'notes': form['notes'].value() or ''
            }
            return JsonResponse({'status': 'success', 'form': form_data})
    
    return render(request, 'companions.html', {'form': form, 'companion': companion})

def companion_delete(request, companion_id):
    """Delete a companion."""
    companion = get_object_or_404(Companion, companion_id=companion_id)
    if request.method == 'POST':
        try:
            log_action(request.user, companion, 'suppression')  # Log before deletion
            companion.delete()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Accompagnant supprimé avec succès.'})
            messages.success(request, 'Accompagnant supprimé avec succès.')
            return redirect('companion_list')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            messages.error(request, f'Erreur lors de la suppression : {str(e)}')
    return redirect('companion_list')

def companion_details(request, companion_id):
    """Display companion details."""
    companion = get_object_or_404(Companion, companion_id=companion_id)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'companion': {
                'companion_id': companion.companion_id,
                'companion_name': companion.companion_name,
                'patient': str(companion.patient),
                'relationship': companion.relationship,
                'start_date': companion.start_date.isoformat() if companion.start_date else '',
                'end_date': companion.end_date.isoformat() if companion.end_date else 'En cours',
                'room': companion.room.room_name if companion.room else 'Non assigné',
                'bed': companion.bed.bed_number if companion.bed else 'Non assigné',
                'accommodation_start_date': companion.accommodation_start_date.isoformat() if companion.accommodation_start_date else '',
                'accommodation_end_date': companion.accommodation_end_date.isoformat() if companion.accommodation_end_date else '',
                'notes': companion.notes
            }
        })
    return render(request, 'companions.html', {'companion': companion})
def reservation_planning(request):
    reservations = Reservation.objects.all()
    patients = Patient.objects.all()
    rooms = Room.objects.all()
    beds = Bed.objects.all()
    reservation_statuses = Reservation.RESERVATION_STATUS
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Réservation créée avec succès.')
            return redirect('hosting:reservation_planning')
        else:
            messages.error(request, 'Erreur lors de la création de la réservation.')
            print(form.errors)  # Debug form errors
    else:
        form = ReservationForm()
    
    # Debug bed statuses
    for bed in beds:
        print(f"Bed {bed.bed_number}: bed_status={bed.bed_status_id}, type={type(bed.bed_status_id)}")
    
    context = {
        'reservations': reservations,
        'patients': patients,
        'rooms': rooms,
        'beds': beds,
        'reservation_statuses': reservation_statuses,
        'form': form,
        'selected_status': request.GET.get('reservation_status', '')
    }
    return render(request, 'calendar.html', context)



def get_calendar_events(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        reservations = Reservation.objects.select_related('patient', 'room', 'bed').all()
        
        reservation_data = []
        for reservation in reservations:
            # Concaténer first_name et last_name
            first_name = reservation.patient.first_name or ""
            last_name = reservation.patient.last_name or ""
            patient_name = f"{first_name} {last_name}".strip()
            
            # Si aucun nom n'est disponible, utiliser une valeur par défaut
            if not patient_name:
                patient_name = "Patient sans nom"
            
            reservation_data.append({
                'start_date': reservation.start_date.strftime('%Y-%m-%d'),
                'end_date': reservation.end_date.strftime('%Y-%m-%d'),
                'patient_name': patient_name,  # Nom complet maintenant
                'reservation_status': reservation.reservation_status,
                'room_name': reservation.room.room_name if reservation.room else '',
                'bed_number': reservation.bed.bed_number if reservation.bed else 'Non assigné'
            })
        
        data = {
            'reservations': reservation_data
        }
        return JsonResponse(data)
    return JsonResponse({'error': 'Invalid request'}, status=400)



def get_calendar_events_alternative(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        reservations = Reservation.objects.select_related('patient', 'room', 'bed').all()
        
        reservation_data = []
        for reservation in reservations:
            patient_name = str(reservation.patient)  
            reservation_data.append({
                'start_date': reservation.start_date.strftime('%Y-%m-%d'),
                'end_date': reservation.end_date.strftime('%Y-%m-%d'),
                'patient_name': patient_name,
                'reservation_status': reservation.reservation_status,
                'room_name': reservation.room.room_name if reservation.room else '',
                'bed_number': reservation.bed.bed_number if reservation.bed else 'Non assigné'
            })
        
        data = {
            'reservations': reservation_data
        }
        return JsonResponse(data)
    return JsonResponse({'error': 'Invalid request'}, status=400)
def hosting_configuration(request):
    room_types = room_type.RoomType.objects.all()
    bed_statuses = bed_status.BedStatus.objects.all()
    room_type_paginator = Paginator(room_types, 5)
    bed_status_paginator = Paginator(bed_statuses, 5)
    room_type_page_number = request.GET.get('room_type_page', 1)
    bed_status_page_number = request.GET.get('bed_status_page', 1)
    room_types_page = room_type_paginator.get_page(room_type_page_number)
    bed_statuses_page = bed_status_paginator.get_page(bed_status_page_number)
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'room_type':
            form = RoomTypeForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Type de chambre créé avec succès.')
                log_action(request.user, form.instance, 'creation')
                return redirect('hosting_configuration')
            else:
                messages.error(request, 'Erreur lors de la création du type de chambre.')
        elif form_type == 'edit_room_type':
            room_type_id = request.POST.get('id')
            try:
                room_type_instance = room_type.RoomType.objects.get(id=room_type_id)
                form = RoomTypeForm(request.POST, instance=room_type_instance)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Type de chambre modifié avec succès.')
                    log_action(request.user, form.instance, 'modification')
                    return redirect('hosting_configuration')
                else:
                    messages.error(request, 'Erreur lors de la modification du type de chambre.')
            except room_type.RoomType.DoesNotExist:
                messages.error(request, 'Type de chambre introuvable.')
        elif form_type == 'delete_room_type':
            room_type_id = request.POST.get('id')
            try:
                room_type_instance = room_type.RoomType.objects.get(id=room_type_id)
                room_type_name = room_type_instance.name
                room_type_instance.delete()
                messages.success(request, f'Type de chambre "{room_type_name}" supprimé avec succès.')
                log_action(request.user, room_type_instance, 'suppression')
                return redirect('hosting_configuration')
            except room_type.RoomType.DoesNotExist:
                messages.error(request, 'Type de chambre introuvable.')
            except Exception as e:
                messages.error(request, 'Erreur lors de la suppression du type de chambre.')
        
        # Création d'un nouveau statut de lit
        elif form_type == 'bed_status':
            form = BedStatusForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Statut de lit créé avec succès.')
                log_action(request.user, form.instance, 'creation')
                return redirect('hosting_configuration')
            else:
                messages.error(request, 'Erreur lors de la création du statut de lit.')
        
        # Modification d'un statut de lit
        elif form_type == 'edit_bed_status':
            bed_status_id = request.POST.get('id')
            try:
                bed_status_instance = bed_status.BedStatus.objects.get(id=bed_status_id)
                form = BedStatusForm(request.POST, instance=bed_status_instance)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Statut de lit modifié avec succès.')
                    log_action(request.user, form.instance, 'modification')
                    return redirect('hosting_configuration')
                else:
                    messages.error(request, 'Erreur lors de la modification du statut de lit.')
            except bed_status.BedStatus.DoesNotExist:
                messages.error(request, 'Statut de lit introuvable.')
        
        # Suppression d'un statut de lit
        elif form_type == 'delete_bed_status':
            bed_status_id = request.POST.get('id')
            try:
                bed_status_instance = bed_status.BedStatus.objects.get(id=bed_status_id)
                bed_status_name = bed_status_instance.name
                bed_status_instance.delete()
                messages.success(request, f'Statut de lit "{bed_status_name}" supprimé avec succès.')
                log_action(request.user, bed_status_instance, 'suppression')
                return redirect('hosting_configuration')
            except bed_status.BedStatus.DoesNotExist:
                messages.error(request, 'Statut de lit introuvable.')
            except Exception as e:
                messages.error(request, 'Erreur lors de la suppression du statut de lit.')
    
    room_type_form = RoomTypeForm()
    bed_status_form = BedStatusForm()
    
    context = {
        'room_types': room_types_page,
        'bed_statuses': bed_statuses_page,
        'room_type_form': room_type_form,
        'bed_status_form': bed_status_form,
    }
    return render(request, 'hosting_configuration.html', context)