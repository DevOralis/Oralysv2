from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
import json

# Create your views here.

@login_required
def dashboard_view(request):
    """
    Vue principale du tableau de bord - Affiche les statistiques HR par défaut
    """
    # Rediriger vers la vue des statistiques HR
    return hr_stats_view(request)


@login_required
def formation_stats_view(request):
    """
    Vue pour afficher les statistiques du module formation dans le dashboard
    """
    try:
        # Import des modèles de formation
        from apps.formation.models import Formation, Session, Inscription, Formateur, Evaluation, Supplier
        
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
        
        # Statistiques dynamiques par type de formation
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
            if type_key:
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
            domaine['domaine__display'] = domaine_choices.get(domaine['domaine'], domaine['domaine'])
        
        # Formations par type avec pourcentages pour le graphique
        formations_par_type = []
        for type_stat in types_with_stats:
            if type_stat['count'] > 0:
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
        today = timezone.now()
        week_end = today + timedelta(days=7)
        upcoming_sessions = Session.objects.filter(
            date_debut__gte=today,
            date_debut__lte=week_end,
            statut__in=['planifiée', 'en_cours']
        )
        
        # Sessions avec places limitées
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
            'types_with_stats': types_with_stats,
            'formations_par_type': formations_par_type,
            'recent_sessions': recent_sessions,
            'formations_par_domaine': formations_par_domaine,
            'top_formateurs': top_formateurs,
            'upcoming_sessions': upcoming_sessions,
            'sessions_places_limitees': sessions_places_limitees,
            'formations_list': formations_list,
            'formateurs_list': formateurs_list,
            'suppliers_list': suppliers_list,
            'domaines_choices': domaines_choices,
        }
        
        return render(request, 'dashboard/formation_stats.html', context)
    
    except Exception as e:
        # En cas d'erreur, afficher une page simple
        context = {
            'error': str(e)
        }
        return render(request, 'dashboard/formation_stats.html', context)


@login_required
def demandes_stats_view(request):
    """
    Vue pour afficher les statistiques du module demandes dans le dashboard
    """
    try:
        # Import des modèles de demandes
        from apps.demandes.models import Priorite, Statut, Produit, DemandeInterne, DemandeProduit, DemandePatient, DemandePatientModel
        from django.db.models import F
        
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
            demandepatient__created_at__gte=timezone.now() - timedelta(days=30)
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
        
        # Types de demandes patients
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
        
        return render(request, 'dashboard/demandes_stats.html', context)
    
    except Exception as e:
        # En cas d'erreur, afficher une page simple
        context = {
            'error': str(e)
        }
        return render(request, 'dashboard/demandes_stats.html', context)


@login_required
def purchases_stats_view(request):
    """
    Vue pour afficher les statistiques du module purchases dans le dashboard
    """
    try:
        # Import des modèles de purchases
        from apps.purchases.models import Supplier, PurchaseOrder, Convention
        from django.db.models import Sum
        from decimal import Decimal
        
        # Statistiques principales
        total_orders = PurchaseOrder.objects.count()
        total_conventions = Convention.objects.count()
        total_suppliers = Supplier.objects.count()
        total_order_amount = PurchaseOrder.objects.aggregate(Sum('amount_total'))['amount_total__sum'] or Decimal('0.00')
        
        # Dernières commandes
        orders = PurchaseOrder.objects.all().select_related('partner', 'currency').order_by('-date_order')[:5]
        
        # Dernières conventions
        conventions = Convention.objects.all().select_related('partner', 'convention_type', 'currency').order_by('-date_start')[:5]
        
        # Tous les fournisseurs
        suppliers = Supplier.objects.all()
        
        # États des commandes
        purchase_order_states = PurchaseOrder.STATE_CHOICES
        
        context = {
            'total_orders': total_orders,
            'total_conventions': total_conventions,
            'total_suppliers': total_suppliers,
            'total_order_amount': "%.2f" % float(total_order_amount),
            'orders': orders,
            'conventions': conventions,
            'suppliers': suppliers,
            'purchase_order_states': purchase_order_states,
            'page_title': 'Dashboard - Achats'
        }
        
        return render(request, 'dashboard/purchases_stats.html', context)
    
    except Exception as e:
        # En cas d'erreur, afficher une page simple
        context = {
            'error': str(e)
        }
        return render(request, 'dashboard/purchases_stats.html', context)


@login_required
def inventory_stats_view(request):
    """
    Vue pour afficher les statistiques du module inventory dans le dashboard
    """
    try:
        # Import des modèles d'inventory
        from apps.inventory.models import Product, StockMove, Category, ProductType
        from django.db.models import Q, F, Sum
        import json
        
        # Statistiques principales
        total_products = Product.objects.filter(active=True).count()
        total_stock_moves = StockMove.objects.count()
        total_categories = Category.objects.count()
        low_stock_products = Product.objects.filter(
            active=True,
            total_quantity_cached__lte=F('stock_minimal')
        ).count()
        
        # Mouvements par statut
        moves_by_status = StockMove.objects.values('state').annotate(
            count=Count('move_id')
        )
        
        # Produits par catégorie
        products_by_category = Category.objects.annotate(
            product_count=Count('product', filter=Q(product__active=True))
        ).filter(product_count__gt=0).order_by('-product_count')[:10]
        
        # Valeur totale du stock
        total_stock_value = Product.objects.filter(active=True).aggregate(
            total_value=Sum(F('total_quantity_cached') * F('standard_price'))
        )['total_value'] or 0
        
        # Mouvements par mois (6 derniers mois)
        moves_by_month = []
        for i in range(6):
            month_start = (timezone.now().replace(day=1) - timedelta(days=30*i)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            count = StockMove.objects.filter(
                date_created__gte=month_start,
                date_created__lte=month_end
            ).count()
            
            moves_by_month.append({
                'month_name': month_start.strftime('%B %Y'),
                'count': count
            })
        
        moves_by_month.reverse()
        
        # Produits récents (5 derniers)
        recent_products = Product.objects.filter(active=True).order_by('-product_id')[:5]
        
        # Mouvements récents (5 derniers)
        recent_moves = StockMove.objects.select_related(
            'operation_type', 'source_location', 'dest_location'
        ).order_by('-date_created')[:5]
        
        # Produits en rupture de stock
        out_of_stock = Product.objects.filter(
            active=True,
            total_quantity_cached=0
        ).count()
        
        # Produits par type
        try:
            products_by_type = ProductType.objects.annotate(
                product_count=Count('product', filter=Q(product__active=True))
            ).filter(product_count__gt=0).order_by('-product_count')[:10]
        except:
            products_by_type = []
        
        # Préparer les données JSON pour les graphiques
        moves_status_json = json.dumps([
            {'status': item['state'], 'count': item['count']} 
            for item in moves_by_status
        ])
        
        products_category_json = json.dumps([
            {'category': category.label, 'count': category.product_count} 
            for category in products_by_category
        ])
        
        moves_month_json = json.dumps([
            {'month_name': month['month_name'], 'count': month['count']} 
            for month in moves_by_month
        ])
        
        products_type_json = json.dumps([
            {'type': ptype.label, 'count': ptype.product_count} 
            for ptype in products_by_type
        ] if products_by_type else [])
        
        stock_status_json = json.dumps([
            {'status': 'Stock normal', 'count': total_products - low_stock_products - out_of_stock},
            {'status': 'Stock faible', 'count': low_stock_products},
            {'status': 'Rupture', 'count': out_of_stock}
        ])
        
        context = {
            'total_products': total_products,
            'total_stock_moves': total_stock_moves,
            'total_categories': total_categories,
            'low_stock_products': low_stock_products,
            'out_of_stock': out_of_stock,
            'total_stock_value': total_stock_value,
            'moves_by_status': moves_by_status,
            'products_by_category': products_by_category,
            'products_by_type': products_by_type,
            'moves_by_month': moves_by_month,
            'recent_products': recent_products,
            'recent_moves': recent_moves,
            'moves_status_json': moves_status_json,
            'products_category_json': products_category_json,
            'moves_month_json': moves_month_json,
            'products_type_json': products_type_json,
            'stock_status_json': stock_status_json,
        }
        
        return render(request, 'dashboard/inventory_stats.html', context)
    
    except Exception as e:
        context = {
            'error': str(e)
        }
        return render(request, 'dashboard/inventory_stats.html', context)


@login_required
def maintenance_stats_view(request):
    """
    Vue pour afficher les statistiques du module maintenance dans le dashboard
    """
    try:
        # Import des modèles et de la vue originale
        from apps.maintenance.views import StatisticsView
        
        # Créer une instance de la vue originale
        stats_view = StatisticsView()
        stats_view.request = request
        
        # Obtenir le contexte
        context = stats_view.get_context_data()
        
        # Rendre avec le template du dashboard
        return render(request, 'dashboard/maintenance_stats.html', context)
    
    except Exception as e:
        context = {
            'error': str(e)
        }
        return render(request, 'dashboard/maintenance_stats.html', context)


@login_required
def parcauto_stats_view(request):
    """
    Vue pour afficher les statistiques du module parcauto dans le dashboard
    """
    try:
        # Import des modèles de parcauto
        from apps.parcauto.models import Vehicule, Affectation, Entretien, Modele, StatutVehicule, TypeVehicule
        from django.db.models import F
        
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

        # Default model statistics
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
        return render(request, 'dashboard/parcauto_stats.html', context)
        
    except Exception as e:
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
            'models': [],
            'model_stats': {'error': str(e)},
            'model_charts_data': json.dumps({}),
        }
        return render(request, 'dashboard/parcauto_stats.html', context)


@login_required
def pharmacy_stats_view(request):
    """
    Vue pour afficher les statistiques du module pharmacy dans le dashboard
    """
    try:
        # Import des modèles de pharmacy
        from apps.pharmacy.models import PharmacyOrder, PharmacySupplier
        from django.db.models import Sum
        
        # Total orders
        total_orders = PharmacyOrder.objects.count()
        
        # Total suppliers
        total_suppliers = PharmacySupplier.objects.count()
        
        # Total order amount
        total_order_amount = PharmacyOrder.objects.aggregate(total=Sum('amount_total'))['total'] or 0.0
        
        # Get all orders for the table
        orders = PharmacyOrder.objects.select_related('supplier', 'currency').order_by('-date_order')[:5]
        
        # Get all suppliers for the filter dropdown
        suppliers = PharmacySupplier.objects.all()
        
        # Get order states for the filter dropdown
        purchase_order_states = PharmacyOrder.STATE_CHOICES
        
        context = {
            'total_orders': total_orders,
            'total_suppliers': total_suppliers,
            'total_order_amount': float(total_order_amount),
            'orders': orders,
            'suppliers': suppliers,
            'purchase_order_states': purchase_order_states,
            'page_title': 'Dashboard - Pharmacie',
        }
        
        return render(request, 'dashboard/pharmacy_stats.html', context)
        
    except Exception as e:
        context = {
            'error': str(e)
        }
        return render(request, 'dashboard/pharmacy_stats.html', context)


@login_required
def recruitment_stats_view(request):
    """
    Vue pour afficher les statistiques du module recruitment dans le dashboard
    """
    try:
        # Import de la fonction originale
        from apps.recruitment.views import recruitment_statistics
        from django.template.response import TemplateResponse
        
        # Appeler la fonction originale pour obtenir le contexte
        response = recruitment_statistics(request)
        
        # Si c'est une TemplateResponse, on peut récupérer le contexte
        if isinstance(response, TemplateResponse):
            context = response.context_data
        else:
            # Sinon on utilise le contexte par défaut
            context = {}
        
        # Rendre avec le template du dashboard
        return render(request, 'dashboard/recruitment_stats.html', context)
    
    except Exception as e:
        context = {
            'error': str(e)
        }
        return render(request, 'dashboard/recruitment_stats.html', context)


@login_required
def patient_stats_view(request):
    """
    Vue pour afficher les statistiques du module patient dans le dashboard
    """
    try:
        # Import des modèles de patient
        from apps.patient.models import Patient, Consultation, Appointment
        
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
        
        # Consultations par spécialité
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
        
        return render(request, 'dashboard/patient_stats.html', context)
    
    except Exception as e:
        context = {
            'error': str(e)
        }
        return render(request, 'dashboard/patient_stats.html', context)


@login_required
def restauration_stats_view(request):
    """
    Vue pour afficher les statistiques du module restauration dans le dashboard
    """
    try:
        # Appeler directement la fonction originale et changer seulement le template
        from apps.Restauration import views as restauration_views
        
        # Récupérer la réponse originale
        original_response = restauration_views.dashboard_restauration(request)
        
        # Extraire le contexte depuis le contenu rendu
        # On va simplement réutiliser la fonction mais avec notre template
        # Pour cela, on va patcher temporairement le render
        from django.shortcuts import render as original_render
        context_captured = {}
        
        def capture_render(request, template_name, context=None):
            context_captured.update(context or {})
            return original_render(request, 'dashboard/restauration_stats.html', context)
        
        # Remplacer temporairement render dans le module
        import apps.Restauration.views
        old_render = apps.Restauration.views.render
        apps.Restauration.views.render = capture_render
        
        # Appeler la fonction
        result = restauration_views.dashboard_restauration(request)
        
        # Restaurer l'original
        apps.Restauration.views.render = old_render
        
        return result
        
    except Exception as e:
        context = {
            'error': str(e)
        }
        return render(request, 'dashboard/restauration_stats.html', context)


@login_required
def hr_stats_view(request):
    """
    Vue pour afficher les statistiques du module hr dans le dashboard
    """
    try:
        # Import des modèles de hr
        from apps.hr.models import Employee, Department, LeaveRequest, PayrollGenerationHistory
        from django.db.models import Q
        
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
        
        leaves_by_month.reverse()
        
        # Préparer les données JSON pour les graphiques
        department_stats_json = json.dumps([
            {'name': dept.name, 'employee_count': dept.employee_count} 
            for dept in department_stats
        ])
        
        leaves_by_month_json = json.dumps([
            {'month_name': month['month_name'], 'count': month['count']} 
            for month in leaves_by_month
        ])
        
        marital_stats_json = json.dumps([
            {'status': dict(Employee.MARITAL_STATUS_CHOICES).get(item['marital_status'], item['marital_status']), 'count': item['count']} 
            for item in marital_stats
        ])
        
        gender_stats_json = json.dumps([
            {'gender': 'H' if item['gender'] == 'H' else 'F' if item['gender'] == 'F' else 'Autre', 'count': item['count']} 
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
        
        return render(request, 'dashboard/hr_stats.html', context)
    
    except Exception as e:
        context = {
            'error': str(e)
        }
        return render(request, 'dashboard/hr_stats.html', context)


@login_required
def hosting_stats_view(request):
    """
    Vue pour afficher les statistiques du module hosting dans le dashboard
    """
    try:
        # Import des modèles de hosting
        from apps.hosting.models import Room, Admission, Reservation
        
        # Statistiques de base
        total_rooms = Room.objects.count()
        occupied_rooms = Room.objects.filter(admissions__discharge_date__isnull=True).distinct().count()
        occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
        admissions = Admission.objects.all().order_by('-admission_date')[:10]
        reservations = Reservation.objects.all().order_by('-start_date')[:10]
        room_types = Room.ROOM_TYPE
        
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
        room_type_counts = Room.objects.values('room_type').annotate(count=Count('room_id')).order_by()
        
        context = {
            'total_rooms': total_rooms,
            'occupied_rooms': occupied_rooms,
            'occupancy_rate': occupancy_rate,
            'admissions': admissions,
            'reservations': reservations,
            'room_types': room_types,
            'admission_counts': admission_counts,
            'room_type_counts': room_type_counts,
        }
        
        return render(request, 'dashboard/hosting_stats.html', context)
    
    except Exception as e:
        # En cas d'erreur, afficher une page simple
        context = {
            'error': str(e)
        }
        return render(request, 'dashboard/hosting_stats.html', context)


@login_required
def therapeutic_activities_stats_view(request):
    """
    Vue pour afficher les statistiques du module therapeutic activities dans le dashboard
    """
    try:
        # Import des modèles de therapeutic activities
        from apps.therapeutic_activities.models import (
            Activity, Session, Participation, ActivityType, 
            ActivityLocation, ErgotherapyEvaluation, 
            CoachingSession, SocialReport
        )
        from apps.hr.models.employee import Employee
        from apps.patient.models import Patient
        
        # Statistiques principales
        total_activities = Activity.objects.filter(is_active=True).count()
        total_sessions = Session.objects.count()
        total_participations = Participation.objects.count()
        
        # Sessions aujourd'hui
        today_sessions = Session.objects.filter(
            date=timezone.now().date(),
            status='planned'
        ).annotate(
            participants_count=Count('participants')
        ).order_by('start_time')
        
        # Sessions à venir
        upcoming_sessions = Session.objects.filter(
            status='planned',
            date__gte=timezone.now().date()
        ).select_related('activity', 'location', 'activity__coach').order_by('date', 'start_time')[:5]
        
        # Statistiques par type d'activité
        activity_types_stats = ActivityType.objects.annotate(
            activities_count_annotation=Count('activity', filter=Q(activity__is_active=True)),
            sessions_count_annotation=Count('activity__sessions')
        ).filter(activities_count_annotation__gt=0).order_by('-sessions_count_annotation')[:5]
        
        # Top coaches
        top_coaches = Activity.objects.values(
            'coach__full_name'
        ).annotate(
            sessions_count=Count('sessions')
        ).filter(
            coach__isnull=False
        ).order_by('-sessions_count')[:5]
        
        # Répartition des sessions par statut
        sessions_by_status = Session.objects.values('status').annotate(
            count=Count('id')
        )
        
        # Participations par statut
        participations_by_status = Participation.objects.values('status').annotate(
            count=Count('id')
        )
        
        # Évolutions sur les derniers mois
        months_ago = 6
        sessions_by_month = []
        for i in range(months_ago):
            month_start = (timezone.now().replace(day=1) - timedelta(days=30*i)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            count = Session.objects.filter(
                date__gte=month_start,
                date__lte=month_end
            ).count()
            
            sessions_by_month.append({
                'month_name': month_start.strftime('%b'),
                'count': count
            })
        
        sessions_by_month.reverse()
        
        # Préparer les données JSON pour les graphiques
        sessions_status_json = json.dumps([
            {'status': item['status'], 'count': item['count']} 
            for item in sessions_by_status
        ])
        
        participations_status_json = json.dumps([
            {'status': item['status'], 'count': item['count']} 
            for item in participations_by_status
        ])
        
        sessions_month_json = json.dumps([
            {'month_name': month['month_name'], 'count': month['count']} 
            for month in sessions_by_month
        ])
        
        context = {
            'page_title': 'Dashboard - Activités Thérapeutiques',
            'total_activities': total_activities,
            'total_sessions': total_sessions,
            'total_participations': total_participations,
            'today_sessions': today_sessions,
            'upcoming_sessions': upcoming_sessions,
            'activity_types_stats': activity_types_stats,
            'top_coaches': top_coaches,
            'sessions_by_status': sessions_by_status,
            'participations_by_status': participations_by_status,
            'sessions_by_month': sessions_by_month,
            'sessions_status_json': sessions_status_json,
            'participations_status_json': participations_status_json,
            'sessions_month_json': sessions_month_json,
        }
        
        return render(request, 'dashboard/therapeutic_activities_stats.html', context)
    
    except Exception as e:
        # En cas d'erreur, afficher une page simple
        context = {
            'page_title': 'Dashboard - Activités Thérapeutiques',
            'error': str(e),
            'total_activities': 0,
            'total_sessions': 0,
            'total_participations': 0,
            'today_sessions': [],
            'upcoming_sessions': [],
            'activity_types_stats': [],
            'top_coaches': [],
        }
        return render(request, 'dashboard/therapeutic_activities_stats.html', context)
