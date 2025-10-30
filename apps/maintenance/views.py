from datetime import timedelta
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Convention, Incident, Intervention, Visiteur, Equipement  
from apps.purchases.models import Supplier
from django.utils.dateparse import parse_datetime, parse_date
from django.views.generic import TemplateView
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.db.models.functions import TruncMonth, TruncYear
import json  
from django.core.paginator import Paginator



class StatisticsView(TemplateView):
    template_name = 'maintenance_statistics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # Statistiques des Conventions
        context.update({
            # Total des conventions
            'total_conventions': Convention.objects.count(),
            
            # Conventions actives vs expirées
            'conventions_actives': Convention.objects.filter(
                date_debut__lte=today, 
                date_fin__gte=today
            ).count(),
            'conventions_expirees': Convention.objects.filter(
                date_fin__lt=today
            ).count(),
            
            # Coût total des conventions
            'cout_total_conventions': Convention.objects.aggregate(
                total=Sum('cout_mensuel')
            )['total'] or 0,
        })
        
        # Données pour les graphiques (formatées en JSON)
        # Conventions par fournisseur
        conventions_supplier = list(Convention.objects.values('supplier__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10])
        
        # Renommer les clés pour éviter les problèmes avec les underscores doubles
        conventions_supplier_renamed = []
        for item in conventions_supplier:
            conventions_supplier_renamed.append({
                'supplier_nom': item['supplier__name'],
                'count': item['count']
            })
        context['conventions_par_supplier_json'] = json.dumps(conventions_supplier_renamed)
        
        # Conventions par type
        conventions_type = list(Convention.objects.values('type_convention')
            .annotate(count=Count('id'))
            .order_by('-count'))
        context['conventions_par_type_json'] = json.dumps(conventions_type)
        
        # Conventions par mois
        conventions_mois = list(Convention.objects.annotate(
            mois=TruncMonth('date_debut')
        ).values('mois').annotate(
            count=Count('id')
        ).order_by('mois')[:12])
        
        # Formatage des dates pour le graphique
        conventions_mois_formatted = []
        for item in conventions_mois:
            if item['mois']:
                conventions_mois_formatted.append({
                    'mois': item['mois'].strftime('%Y-%m-%d'),
                    'count': item['count']
                })
        
        context['conventions_par_mois_json'] = json.dumps(conventions_mois_formatted)
        
        # Statistiques des Visiteurs
        from datetime import timedelta
        
        # Visiteurs cette semaine (7 derniers jours)
        semaine_debut = today - timedelta(days=7)
        visiteurs_semaine = Visiteur.objects.filter(date_entree__date__gte=semaine_debut).count()
        
        # Visiteurs ce mois (30 derniers jours)
        mois_debut = today - timedelta(days=30)
        visiteurs_mois = Visiteur.objects.filter(date_entree__date__gte=mois_debut).count()
        
        # Durée moyenne des visites
        visiteurs_termines = Visiteur.objects.filter(date_sortie__isnull=False)
        duree_totale = timedelta(0)
        count_visiteurs = 0
        
        for visiteur in visiteurs_termines:
            if visiteur.date_sortie and visiteur.date_entree:
                duree_totale += visiteur.date_sortie - visiteur.date_entree
                count_visiteurs += 1
        
        if count_visiteurs > 0:
            duree_moyenne = duree_totale / count_visiteurs
            duree_heures = int(duree_moyenne.total_seconds() // 3600)
            duree_minutes = int((duree_moyenne.total_seconds() % 3600) // 60)
            duree_moyenne_formatted = f"{duree_heures}h {duree_minutes}m"
        else:
            duree_moyenne_formatted = "N/A"
        
        # Visiteurs par motif (top 5)
        visiteurs_par_motif = list(Visiteur.objects.values('motif_visite')
            .annotate(count=Count('id'))
            .order_by('-count')[:5])
        
        # Renommer les clés pour éviter les problèmes
        visiteurs_par_motif_renamed = []
        for item in visiteurs_par_motif:
            visiteurs_par_motif_renamed.append({
                'motif_visite': item['motif_visite'],
                'count': item['count']
            })
        
        # Données pour le graphique de durée des visites par période
        visiteurs_duree_periode = []
        for i in range(7):  # 7 derniers jours
            date_cible = today - timedelta(days=i)
            visiteurs_jour = Visiteur.objects.filter(
                date_entree__date=date_cible,
                date_sortie__isnull=False
            )
            
            duree_totale_jour = timedelta(0)
            count_jour = 0
            
            for visiteur in visiteurs_jour:
                if visiteur.date_sortie and visiteur.date_entree:
                    duree_totale_jour += visiteur.date_sortie - visiteur.date_entree
                    count_jour += 1
            
            if count_jour > 0:
                duree_moyenne_jour = duree_totale_jour / count_jour
                duree_minutes = int(duree_moyenne_jour.total_seconds() / 60)
            else:
                duree_minutes = 0
                
            visiteurs_duree_periode.append({
                'date': date_cible.strftime('%Y-%m-%d'),
                'duree_moyenne': duree_minutes
            })
        
        # Inverser pour avoir les dates dans l'ordre chronologique
        visiteurs_duree_periode.reverse()
        
        context.update({
            'total_visiteurs': Visiteur.objects.count(),
            'visiteurs_presents': Visiteur.objects.filter(date_sortie__isnull=True).count(),
            'visiteurs_aujourd_hui': Visiteur.objects.filter(date_entree__date=today).count(),
            'visiteurs_semaine': visiteurs_semaine,
            'visiteurs_mois': visiteurs_mois,
            'duree_moyenne_visites': duree_moyenne_formatted,
            'visiteurs_par_motif': visiteurs_par_motif,
        })
        
        # Données JSON pour les graphiques des visiteurs
        context['visiteurs_par_motif_json'] = json.dumps(visiteurs_par_motif_renamed)
        context['visiteurs_duree_periode_json'] = json.dumps(visiteurs_duree_periode)
        
        # Statistiques des Incidents
        from datetime import timedelta
        
        # Incidents par statut
        incidents_par_statut = list(Incident.objects.values('statut')
            .annotate(count=Count('id'))
            .order_by('-count'))
        
        # Incidents par type
        incidents_par_type = list(Incident.objects.values('type')
            .annotate(count=Count('id'))
            .order_by('-count'))
        
        # Incidents par gravité
        incidents_par_gravite = list(Incident.objects.values('gravite')
            .annotate(count=Count('id'))
            .order_by('-count'))
        
        # Incidents par équipement (top 10)
        incidents_par_equipement = list(Incident.objects.values('equipement__nom')
            .annotate(count=Count('id'))
            .order_by('-count')[:10])
        
        # Renommer les clés pour éviter les problèmes
        incidents_par_equipement_renamed = []
        for item in incidents_par_equipement:
            incidents_par_equipement_renamed.append({
                'equipement_nom': item['equipement__nom'],
                'count': item['count']
            })
        
        # Incidents par période
        incidents_aujourd_hui = Incident.objects.filter(date_declaration__date=today).count()
        semaine_debut = today - timedelta(days=7)
        incidents_semaine = Incident.objects.filter(date_declaration__date__gte=semaine_debut).count()
        mois_debut = today - timedelta(days=30)
        incidents_mois = Incident.objects.filter(date_declaration__date__gte=mois_debut).count()
        
        # Incidents par année
        incidents_par_annee = list(Incident.objects.annotate(
            annee=TruncYear('date_declaration')
        ).values('annee').annotate(
            count=Count('id')
        ).order_by('annee'))
        
        # Formater les dates pour JSON
        incidents_par_annee_formatted = []
        for item in incidents_par_annee:
            if item['annee']:
                incidents_par_annee_formatted.append({
                    'annee': item['annee'].strftime('%Y'),
                    'count': item['count']
                })
        
        # Incidents non résolus
        incidents_non_resolus = Incident.objects.exclude(statut='resolu').count()
        
        context.update({
            'total_incidents': Incident.objects.count(),
            'incidents_ouverts': Incident.objects.filter(statut__in=['ouvert', 'en_cours']).count(),
            'incidents_resolus': Incident.objects.filter(statut='resolu').count(),
            'incidents_par_statut': incidents_par_statut,
            'incidents_par_type': incidents_par_type,
            'incidents_par_gravite': incidents_par_gravite,
            'incidents_par_equipement': incidents_par_equipement,
            'incidents_aujourd_hui': incidents_aujourd_hui,
            'incidents_semaine': incidents_semaine,
            'incidents_mois': incidents_mois,
            'incidents_par_annee': incidents_par_annee,
            'incidents_non_resolus': incidents_non_resolus,
        })
        
        # Données JSON pour les graphiques des incidents
        context['incidents_par_statut_json'] = json.dumps(incidents_par_statut)
        context['incidents_par_type_json'] = json.dumps(incidents_par_type)
        context['incidents_par_gravite_json'] = json.dumps(incidents_par_gravite)
        context['incidents_par_equipement_json'] = json.dumps(incidents_par_equipement_renamed)
        context['incidents_par_annee_json'] = json.dumps(incidents_par_annee_formatted)
        
        # Statistiques des Interventions
        interventions = Intervention.objects.all()
        
        # KPI Cards
        context.update({
            'total_interventions': interventions.count(),
            'interventions_planifiees': interventions.filter(statut='planifiee').count(),
            'interventions_en_cours': interventions.filter(statut='en_cours').count(),
            'interventions_terminees': interventions.filter(statut='terminee').count(),
        })
        
        # Données pour les graphiques des interventions
        # Interventions par statut
        interventions_par_statut = list(interventions.values('statut')
            .annotate(count=Count('id'))
            .order_by('-count'))
        
        # Interventions par type
        interventions_par_type = list(interventions.values('type_intervention')
            .annotate(count=Count('id'))
            .order_by('-count'))
        
        # Interventions par criticité
        interventions_par_criticite = list(interventions.values('criticite')
            .annotate(count=Count('id'))
            .order_by('-count'))
        
        # Interventions par fournisseur
        interventions_par_supplier = list(interventions.values('supplier__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10])
        
        # Renommer les clés pour éviter les problèmes
        interventions_par_supplier_renamed = []
        for item in interventions_par_supplier:
            interventions_par_supplier_renamed.append({
                'supplier_nom': item['supplier__name'],
                'count': item['count']
            })
        
        # Interventions par équipement
        interventions_par_equipement = list(interventions.values('equipement__nom')
            .annotate(count=Count('id'))
            .order_by('-count')[:10])
        
        # Renommer les clés pour éviter les problèmes
        interventions_par_equipement_renamed = []
        for item in interventions_par_equipement:
            interventions_par_equipement_renamed.append({
                'equipement_nom': item['equipement__nom'],
                'count': item['count']
            })
        
        # Interventions par mois
        interventions_par_mois = list(interventions.annotate(
            mois=TruncMonth('date_intervention')
        ).values('mois').annotate(
            count=Count('id')
        ).order_by('mois')[:12])
        
        # Formater les dates pour le graphique
        interventions_par_mois_formatted = []
        for item in interventions_par_mois:
            if item['mois']:
                interventions_par_mois_formatted.append({
                    'mois': item['mois'].strftime('%Y-%m-%d'),
                    'count': item['count']
                })
        
        # Interventions par période (jour, semaine, mois)
        interventions_aujourd_hui = interventions.filter(date_intervention__date=today).count()
        semaine_debut = today - timedelta(days=7)
        interventions_semaine = interventions.filter(date_intervention__date__gte=semaine_debut).count()
        mois_debut = today - timedelta(days=30)
        interventions_mois = interventions.filter(date_intervention__date__gte=mois_debut).count()
        
        # Interventions par type et criticité
        interventions_preventives_faible = interventions.filter(
            type_intervention='preventive', criticite='faible'
        ).count()
        interventions_preventives_moyenne = interventions.filter(
            type_intervention='preventive', criticite='moyenne'
        ).count()
        interventions_preventives_haute = interventions.filter(
            type_intervention='preventive', criticite='haute'
        ).count()
        interventions_correctives_faible = interventions.filter(
            type_intervention='corrective', criticite='faible'
        ).count()
        interventions_correctives_moyenne = interventions.filter(
            type_intervention='corrective', criticite='moyenne'
        ).count()
        interventions_correctives_haute = interventions.filter(
            type_intervention='corrective', criticite='haute'
        ).count()
        
        # Ajouter toutes les variables au contexte
        context.update({
            'interventions_aujourd_hui': interventions_aujourd_hui,
            'interventions_semaine': interventions_semaine,
            'interventions_mois': interventions_mois,
            'interventions_preventives_faible': interventions_preventives_faible,
            'interventions_preventives_moyenne': interventions_preventives_moyenne,
            'interventions_preventives_haute': interventions_preventives_haute,
            'interventions_correctives_faible': interventions_correctives_faible,
            'interventions_correctives_moyenne': interventions_correctives_moyenne,
            'interventions_correctives_haute': interventions_correctives_haute,
        })
        
        # Données JSON pour les graphiques des interventions
        context['interventions_par_statut_json'] = json.dumps(interventions_par_statut)
        context['interventions_par_type_json'] = json.dumps(interventions_par_type)
        context['interventions_par_criticite_json'] = json.dumps(interventions_par_criticite)
        context['interventions_par_supplier_json'] = json.dumps(interventions_par_supplier_renamed)
        context['interventions_par_equipement_json'] = json.dumps(interventions_par_equipement_renamed)
        context['interventions_par_mois_json'] = json.dumps(interventions_par_mois_formatted)
        
        return context

def menu_maintenance(request):
    return render(request, 'menu_maintenance.html')

class ConventionListView(ListView):
    model = Convention
    template_name = 'convention_crud.html'
    context_object_name = 'conventions'
    paginate_by = 5

    def get_queryset(self):
        queryset = Convention.objects.select_related('supplier').all().order_by('-date_debut')
        query = self.request.GET.get('q')
        type_filter = self.request.GET.get('type')
        
        if query:
            queryset = queryset.filter(supplier__name__icontains=query)
        if type_filter:
            queryset = queryset.filter(type_convention=type_filter)
            
        return queryset

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['convention_type_choices'] = Convention.TYPE_CHOICES
        context['filtre_type'] = self.request.GET.get('type')
        # Ajouter la liste des prestataires pour le select
        context['prestataires'] = Supplier.objects.all().order_by('name')
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        
        if action == 'add_convention':
            return self.add_convention(request)
        elif action == 'edit_convention':
            return self.edit_convention(request)
        elif action == 'delete_convention':
            return self.delete_convention(request)
        
        return self.get(request, *args, **kwargs)
    
    def add_convention(self, request):
        try:
            prestataire_nom = request.POST.get('prestataire')
            supplier, created = Supplier.objects.get_or_create(name=prestataire_nom)
            fichier = request.FILES.get('fichier')

            # Parse and validate dates
            date_debut_str = request.POST.get('date_debut')
            date_fin_str = request.POST.get('date_fin')
            date_debut = parse_date(date_debut_str) if date_debut_str else None
            date_fin = parse_date(date_fin_str) if date_fin_str else None

            if not date_debut or not date_fin:
                messages.error(request, "Les dates de début et de fin sont obligatoires.")
                return redirect('maintenance:convention_list')

            if date_fin < date_debut:
                messages.error(request, "La date de fin doit être postérieure ou égale à la date de début.")
                return redirect('maintenance:convention_list')

            Convention.objects.create(
                supplier=supplier,
                type_convention=request.POST.get('type_convention'),
                date_debut=date_debut,
                date_fin=date_fin,
                cout_mensuel=request.POST.get('cout_mensuel') or None,
                description=request.POST.get('description', ''),
                fichier=fichier
            )

            messages.success(request, f'Convention avec {supplier.name} créée avec succès!')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création de la convention: {str(e)}')
        
        return redirect('maintenance:convention_list')
    
    def edit_convention(self, request):
        try:
            convention_id = request.POST.get('convention_id')
            convention = get_object_or_404(Convention, id=convention_id)

            prestataire_nom = request.POST.get('prestataire')
            supplier, created = Supplier.objects.get_or_create(name=prestataire_nom)

            # Parse and validate dates
            date_debut_str = request.POST.get('date_debut')
            date_fin_str = request.POST.get('date_fin')
            date_debut = parse_date(date_debut_str) if date_debut_str else None
            date_fin = parse_date(date_fin_str) if date_fin_str else None

            if not date_debut or not date_fin:
                messages.error(request, "Les dates de début et de fin sont obligatoires.")
                return redirect('maintenance:convention_list')

            if date_fin < date_debut:
                messages.error(request, "La date de fin doit être postérieure ou égale à la date de début.")
                return redirect('maintenance:convention_list')

            convention.supplier = supplier
            convention.type_convention = request.POST.get('type_convention')
            convention.date_debut = date_debut
            convention.date_fin = date_fin
            convention.cout_mensuel = request.POST.get('cout_mensuel') or None
            convention.description = request.POST.get('description', '')

           
            fichier = request.FILES.get('fichier')
            if fichier:
                convention.fichier = fichier

            convention.save()

            messages.success(request, f'Convention avec {supplier.name} modifiée avec succès!')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification de la convention: {str(e)}')
        
        return redirect('maintenance:convention_list')

    
    def delete_convention(self, request):
        try:
            convention_id = request.POST.get('convention_id')
            convention = get_object_or_404(Convention, id=convention_id)
            supplier_nom = convention.supplier.name
            convention.delete()
            
            messages.success(request, f'Convention avec {supplier_nom} supprimée avec succès!')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression de la convention: {str(e)}')
        
        return redirect('maintenance:convention_list')


class ConventionCreateView(CreateView):
    model = Convention
    template_name = 'convention_form.html'
    fields = ['supplier', 'type_convention', 'date_debut', 'date_fin', 'cout_mensuel', 'description']
    success_url = reverse_lazy('maintenance:convention_list')

class ConventionUpdateView(UpdateView):
    model = Convention
    template_name = 'convention_form.html'
    fields = ['supplier', 'type_convention', 'date_debut', 'date_fin', 'cout_mensuel', 'description']
    success_url = reverse_lazy('maintenance:convention_list')

class ConventionDetailView(DetailView):
    model = Convention
    template_name = 'convention_detail.html'
    context_object_name = 'convention'

class ConventionDeleteView(DeleteView):
    model = Convention
    template_name = 'convention_confirm_delete.html'
    success_url = reverse_lazy('maintenance:convention_list')

class VisiteurListView(ListView):
    model = Visiteur
    template_name = 'visiteur_list.html'
    context_object_name = 'visiteurs'
    paginate_by = 5
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        status = self.request.GET.get('status')
        queryset = Visiteur.objects.all()
        if query:
            queryset = queryset.filter(
                Q(nom__icontains=query) |
                Q(prenom__icontains=query) |
                Q(email__icontains=query) |
                Q(telephone__icontains=query) |
                Q(motif_visite__icontains=query)
            )
        if status == 'present':
            queryset = queryset.filter(date_sortie__isnull=True)
        elif status == 'sorti':
            queryset = queryset.filter(date_sortie__isnull=False)
        return queryset
    
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        
        if action == 'add_visiteur':
            return self.add_visiteur(request)
        elif action == 'edit_visiteur':
            return self.edit_visiteur(request)
        elif action == 'delete_visiteur':
            return self.delete_visiteur(request)
        
        return redirect('maintenance:visiteur_list')
    
    def add_visiteur(self, request):
        try:
            visiteur = Visiteur.objects.create(
                nom=request.POST.get('nom'),
                prenom=request.POST.get('prenom'),
                email=request.POST.get('email') or None,
                telephone=request.POST.get('telephone') or None,
                motif_visite=request.POST.get('motif_visite') or None
            )
            messages.success(request, f'Visiteur {visiteur.nom} {visiteur.prenom} ajouté avec succès.')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'ajout du visiteur: {str(e)}')
        
        return redirect('maintenance:visiteur_list')
    
    def edit_visiteur(self, request):
        try:
            visiteur_id = request.POST.get('visiteur_id')
            visiteur = get_object_or_404(Visiteur, id=visiteur_id)
            
            visiteur.nom = request.POST.get('nom')
            visiteur.prenom = request.POST.get('prenom')
            visiteur.email = request.POST.get('email') or None
            visiteur.telephone = request.POST.get('telephone') or None
            visiteur.motif_visite = request.POST.get('motif_visite') or None
            
            date_sortie_str = request.POST.get('date_sortie')
            if date_sortie_str:
                date_sortie = parse_datetime(date_sortie_str)
                if date_sortie is None:
                    messages.error(request, "Format de date de sortie invalide.")
                    return redirect('maintenance:visiteur_list')
                # Normaliser et valider l'ordre chronologique
                if timezone.is_naive(date_sortie):
                    date_sortie = timezone.make_aware(date_sortie, timezone.get_current_timezone())
                date_entree = visiteur.date_entree
                if timezone.is_naive(date_entree):
                    date_entree = timezone.make_aware(date_entree, timezone.get_current_timezone())
                if date_sortie < date_entree:
                    messages.error(request, "La date de sortie doit être postérieure ou égale à la date d'entrée.")
                    return redirect('maintenance:visiteur_list')
                visiteur.date_sortie = date_sortie
            else:
                visiteur.date_sortie = None
            
            visiteur.save()
            messages.success(request, f'Visiteur {visiteur.nom} {visiteur.prenom} modifié avec succès.')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification du visiteur: {str(e)}')
        
        return redirect('maintenance:visiteur_list')
    
    def delete_visiteur(self, request):
        try:
            visiteur_id = request.POST.get('visiteur_id')
            visiteur = get_object_or_404(Visiteur, id=visiteur_id)
            visiteur_name = f"{visiteur.nom} {visiteur.prenom}"
            visiteur.delete()
            messages.success(request, f'Visiteur {visiteur_name} supprimé avec succès.')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression du visiteur: {str(e)}')
        
        return redirect('maintenance:visiteur_list')

class VisiteurCreateView(CreateView):
    model = Visiteur
    fields = ['nom', 'prenom', 'email', 'telephone', 'motif_visite']
    template_name = 'visiteur_form.html'
    success_url = reverse_lazy('maintenance:visiteur_list')

class IncidentListView(ListView):
    model = Incident
    template_name = 'incident_list.html'
    context_object_name = 'incidents'
    paginate_by = 5
    ordering = ['-date_declaration']
    def get_queryset(self):
        queryset = super().get_queryset()
        statut = self.request.GET.get("statut")
        type_incident = self.request.GET.get("type")
        search_query = self.request.GET.get("q")
        if statut:
            queryset = queryset.filter(statut=statut)
        if type_incident:
            queryset = queryset.filter(type=type_incident)
        if search_query:
            queryset = queryset.filter(
                Q(equipement__nom__icontains=search_query)
                | Q(equipement__reference__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(type__icontains=search_query)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Récupérer tous les équipements pour le select
        context['equipements'] = Equipement.objects.all().order_by('nom')
        # Passer les choix
        context['incident_type_choices'] = Incident.TYPE_CHOICES
        context['incident_statut_choices'] = Incident.STATUT_CHOICES
        context['incident_gravite_choices'] = Incident.GRAVITE_CHOICES
        return context
    
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        
        if action == 'add_incident':
            return self.add_incident(request)
        elif action == 'edit_incident':
            return self.edit_incident(request)
        elif action == 'delete_incident':
            return self.delete_incident(request)
        
        return self.get(request, *args, **kwargs)
    
    def add_incident(self, request):
        try:
            equipement_id = request.POST.get('equipement')
            date_declaration = request.POST.get('date_declaration')
            type_incident = request.POST.get('type')
            statut = request.POST.get('statut')
            gravite = request.POST.get('gravite', 'faible')
            description = request.POST.get('description', '')
            
            # Validation des champs requis
            if not all([equipement_id, date_declaration, type_incident, statut]):
                messages.error(request, 'Tous les champs obligatoires doivent être remplis.')
                return redirect('maintenance:incident_list')
            
            # Vérifier que l'équipement existe
            equipement = get_object_or_404(Equipement, id=equipement_id)
            
            # Créer l'incident
            incident = Incident.objects.create(
                equipement=equipement,
                date_declaration=date_declaration,
                type=type_incident,
                statut=statut,
                gravite=gravite,
                description=description
            )
            
            messages.success(request, f'Incident #{incident.id} créé avec succès pour {equipement.nom}.')
            
        except Equipement.DoesNotExist:
            messages.error(request, 'L\'équipement sélectionné n\'existe pas.')
        except Exception as e:
            messages.error(request, f'Erreur lors de la création de l\'incident: {str(e)}')
        
        return redirect('maintenance:incident_list')
    
    def edit_incident(self, request):
        try:
            incident_id = request.POST.get('incident_id')
            equipement_id = request.POST.get('equipement')
            date_declaration = request.POST.get('date_declaration')
            type_incident = request.POST.get('type')
            statut = request.POST.get('statut')
            gravite = request.POST.get('gravite', 'faible')
            description = request.POST.get('description', '')
            
            # Validation des champs requis
            if not all([incident_id, equipement_id, date_declaration, type_incident, statut]):
                messages.error(request, 'Tous les champs obligatoires doivent être remplis.')
                return redirect('maintenance:incident_list')
            
            # Vérifier que l'incident et l'équipement existent
            incident = get_object_or_404(Incident, id=incident_id)
            equipement = get_object_or_404(Equipement, id=equipement_id)
            
            # Mettre à jour l'incident
            incident.equipement = equipement
            incident.date_declaration = date_declaration
            incident.type = type_incident
            incident.statut = statut
            incident.gravite = gravite
            incident.description = description
            incident.save()
            
            messages.success(request, f'Incident #{incident.id} modifié avec succès.')
            
        except (Incident.DoesNotExist, Equipement.DoesNotExist):
            messages.error(request, 'L\'incident ou l\'équipement sélectionné n\'existe pas.')
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification de l\'incident: {str(e)}')
        
        return redirect('maintenance:incident_list')
    
    def delete_incident(self, request):
        try:
            incident_id = request.POST.get('incident_id')
            
            if not incident_id:
                messages.error(request, 'ID de l\'incident manquant.')
                return redirect('maintenance:incident_list')
            
            incident = get_object_or_404(Incident, id=incident_id)
            incident_info = f"#{incident.id} ({incident.equipement.nom})"
            incident.delete()
            
            messages.success(request, f'Incident {incident_info} supprimé avec succès.')
            
        except Incident.DoesNotExist:
            messages.error(request, 'L\'incident sélectionné n\'existe pas.')
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression de l\'incident: {str(e)}')
        
        return redirect('maintenance:incident_list')

class IncidentCreateView(CreateView):
    model = Incident
    fields = ['equipement', 'date_declaration', 'type', 'statut', 'gravite', 'description']
    template_name = 'incident_form.html'
    success_url = reverse_lazy('maintenance:incident_list')

class IncidentUpdateView(UpdateView):
    model = Incident
    fields = ['equipement', 'date_declaration', 'type', 'statut', 'gravite', 'description']
    template_name = 'incident_form.html'
    success_url = reverse_lazy('maintenance:incident_list')

class IncidentDetailView(DetailView):
    model = Incident
    template_name = 'incident_detail.html'
    context_object_name = 'incident'

class IncidentDeleteView(DeleteView):
    model = Incident
    template_name = 'incident_confirm_delete.html'
    success_url = reverse_lazy('maintenance:incident_list')


    
class ConfigurationView(ListView):
    template_name = 'config.html'
    model = Equipement
    context_object_name = 'equipements'
    paginate_by = 5
    ordering = ['-date_acquisition']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Les équipements sont maintenant automatiquement fournis par ListView
        # via context_object_name et pagination
        return context

    def post(self, request, *args, **kwargs):
        action = None
        
        # Déterminer l'action à partir des champs cachés du formulaire
        if request.POST.get('ajouter_equipement'):
            action = 'add'
        elif request.POST.get('modifier_equipement'):
            action = 'edit'
        elif request.POST.get('supprimer_equipement'):
            action = 'delete'
        
        if action == 'add':
            return self.add_equipement(request)
        elif action == 'edit':
            return self.edit_equipement(request)
        elif action == 'delete':
            return self.delete_equipement(request)
        
        return redirect('maintenance:configuration')
    
    def add_equipement(self, request):
        try:
            Equipement.objects.create(
                nom=request.POST.get('nom'),
                reference=request.POST.get('reference'),
                date_acquisition=request.POST.get('date_acquisition'),
                emplacement=request.POST.get('emplacement'),
                etat=request.POST.get('etat')
            )
            messages.success(request, "Équipement ajouté avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur lors de l'ajout de l'équipement : {str(e)}")
        return redirect('maintenance:configuration')
    
    def edit_equipement(self, request):
        try:
            equipement_id = request.POST.get('equipement_id')
            equipement = get_object_or_404(Equipement, id=equipement_id)
            
            equipement.nom = request.POST.get('nom')
            equipement.reference = request.POST.get('reference')
            equipement.date_acquisition = request.POST.get('date_acquisition')
            equipement.emplacement = request.POST.get('emplacement')
            equipement.etat = request.POST.get('etat')
            
            equipement.save()
            messages.success(request, f"Équipement '{equipement.nom}' modifié avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur lors de la modification de l'équipement : {str(e)}")
        return redirect('maintenance:configuration')
    
    def delete_equipement(self, request):
        try:
            equipement_id = request.POST.get('equipement_id')
            equipement = get_object_or_404(Equipement, id=equipement_id)
            equipement_nom = equipement.nom
            equipement.delete()
            messages.success(request, f"Équipement '{equipement_nom}' supprimé avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression de l'équipement : {str(e)}")
        return redirect('maintenance:configuration')
    
class InterventionListView(ListView):
    template_name = 'intervention_list.html'
    model = Intervention
    context_object_name = 'interventions'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        statut = self.request.GET.get("statut")
        criticite = self.request.GET.get("criticite")
        search_query = self.request.GET.get("q")
        if statut:
            queryset = queryset.filter(statut=statut)
        if criticite:
            queryset = queryset.filter(criticite=criticite)
        if search_query:
            queryset = queryset.filter(
                Q(equipement__nom__icontains=search_query)
                | Q(equipement__reference__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(supplier__name__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['equipements'] = Equipement.objects.all()
        # Ajouter la liste des prestataires pour le select
        context['prestataires'] = Supplier.objects.all().order_by('name')
        context['filtre_statut'] = self.request.GET.get("statut")
        context['filtre_criticite'] = self.request.GET.get("criticite")
        return context


    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')

        if action == 'add':
            try:
                equipement = get_object_or_404(Equipement, pk=request.POST.get('equipement'))
                supplier = get_object_or_404(Supplier, pk=request.POST.get('prestataire'))
                type_intervention = request.POST.get('type_intervention', 'preventive')
                if type_intervention not in ['preventive', 'corrective']:
                    type_intervention = 'preventive'
                criticite = request.POST.get('criticite', 'moyenne')
                if criticite not in ['faible', 'moyenne', 'haute']:
                    criticite = 'moyenne'
                
                Intervention.objects.create(
                    equipement=equipement,
                    supplier=supplier,
                    date_intervention=request.POST.get('date_intervention'),
                    type_intervention=type_intervention,
                    criticite=criticite,
                    description=request.POST.get('description', ''),
                    statut=request.POST.get('statut', 'planifiee')
                )
                messages.success(request, "Intervention ajoutée avec succès.")
            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout : {str(e)}")

        elif action == 'edit':
            try:
                # Récupérer l'ID de l'intervention à modifier
                intervention_id = request.POST.get('id')
                if not intervention_id:
                    messages.error(request, "ID de l'intervention manquant.")
                    return redirect('maintenance:intervention_list')
                
                # Récupérer l'intervention existante
                intervention = get_object_or_404(Intervention, pk=intervention_id)
                
                # Récupérer et valider l'équipement
                equipement_id = request.POST.get('equipement')
                if equipement_id:
                    equipement = get_object_or_404(Equipement, pk=equipement_id)
                    intervention.equipement = equipement
                
                # Récupérer et valider le prestataire
                prestataire_id = request.POST.get('prestataire')
                if prestataire_id:
                    supplier = get_object_or_404(Supplier, pk=prestataire_id)
                    intervention.supplier = supplier
                else:
                    intervention.supplier = None
                
                # Récupérer et valider la date d'intervention
                date_intervention = request.POST.get('date_intervention')
                if date_intervention:
                    intervention.date_intervention = date_intervention
                
                # Récupérer et valider le statut
                statut = request.POST.get('statut')
                if statut in ['planifiee', 'en_cours', 'terminee']:
                    intervention.statut = statut
                
                # Récupérer et valider le type d'intervention
                type_intervention = request.POST.get('type_intervention')
                if type_intervention in ['preventive', 'corrective']:
                    intervention.type_intervention = type_intervention
                
                # Récupérer et valider la criticité
                criticite = request.POST.get('criticite')
                if criticite in ['faible', 'moyenne', 'haute']:
                    intervention.criticite = criticite
                
                # Récupérer et valider la description
                description = request.POST.get('description', '')
                intervention.description = description
                
                # Sauvegarder les modifications
                intervention.save()
                messages.success(request, f"Intervention #{intervention.id} modifiée avec succès.")
                
            except Intervention.DoesNotExist:
                messages.error(request, "L'intervention sélectionnée n'existe pas.")
            except Equipement.DoesNotExist:
                messages.error(request, "L'équipement sélectionné n'existe pas.")
            except Supplier.DoesNotExist:
                messages.error(request, "Le prestataire sélectionné n'existe pas.")
            except Exception as e:
                messages.error(request, f"Erreur lors de la modification : {str(e)}")

        elif action == 'delete':
            try:
                intervention_id = request.POST.get('id')
                if not intervention_id:
                    messages.error(request, "ID de l'intervention manquant.")
                    return redirect('maintenance:intervention_list')
                
                intervention = get_object_or_404(Intervention, pk=intervention_id)
                intervention_info = f"#{intervention.id} ({intervention.equipement.nom})"
                intervention.delete()
                messages.success(request, f"Intervention {intervention_info} supprimée avec succès.")
            except Intervention.DoesNotExist:
                messages.error(request, "L'intervention sélectionnée n'existe pas.")
            except Exception as e:
                messages.error(request, f"Erreur lors de la suppression : {str(e)}")

        return redirect('maintenance:intervention_list')


def configuration(request):
    """Vue pour la configuration des équipements et prestataires"""
    tab = request.GET.get('tab', 'equipements')
    
    if request.method == 'POST':
        # Gestion des équipements
        if 'ajouter_equipement' in request.POST:
            nom = request.POST.get('nom')
            reference = request.POST.get('reference')
            date_acquisition = request.POST.get('date_acquisition')
            emplacement = request.POST.get('emplacement')
            etat = request.POST.get('etat', 'bon')
            
            if nom and reference and date_acquisition and emplacement:
                Equipement.objects.create(
                    nom=nom,
                    reference=reference,
                    date_acquisition=date_acquisition,
                    emplacement=emplacement,
                    etat=etat
                )
                messages.success(request, f'Équipement {nom} ajouté avec succès!')
            else:
                messages.error(request, 'Tous les champs obligatoires doivent être remplis.')
            
            return redirect('maintenance:configuration')
        
        elif 'modifier_equipement' in request.POST:
            equipement_id = request.POST.get('equipement_id')
            equipement = get_object_or_404(Equipement, id=equipement_id)
            
            equipement.nom = request.POST.get('nom')
            equipement.reference = request.POST.get('reference')
            equipement.date_acquisition = request.POST.get('date_acquisition')
            equipement.emplacement = request.POST.get('emplacement')
            equipement.etat = request.POST.get('etat')
            equipement.save()
            
            messages.success(request, f'Équipement {equipement.nom} modifié avec succès!')
            return redirect('maintenance:configuration')
        
        elif 'supprimer_equipement' in request.POST:
            equipement_id = request.POST.get('equipement_id')
            equipement = get_object_or_404(Equipement, id=equipement_id)
            nom = equipement.nom
            equipement.delete()
            
            messages.success(request, f'Équipement {nom} supprimé avec succès!')
            return redirect('maintenance:configuration')
        
        # Gestion des prestataires
        elif 'ajouter_prestataire' in request.POST:
            nom = request.POST.get('nom')
            contact = request.POST.get('contact')
            adresse = request.POST.get('adresse')
            
            if nom:
                Supplier.objects.create(
                    name=nom,
                    phone=contact,
                    street=adresse
                )
                messages.success(request, f'Prestataire {nom} ajouté avec succès!')
            else:
                messages.error(request, 'Le nom du prestataire est obligatoire.')
            
            return redirect('maintenance:configuration')
        
        elif 'modifier_prestataire' in request.POST:
            prestataire_id = request.POST.get('prestataire_id')
            prestataire = get_object_or_404(Supplier, id=prestataire_id)
            
            prestataire.name = request.POST.get('nom')
            prestataire.phone = request.POST.get('contact')
            prestataire.street = request.POST.get('adresse')
            prestataire.save()
            
            messages.success(request, f'Prestataire {prestataire.name} modifié avec succès!')
            return redirect('maintenance:configuration')
        
        elif 'supprimer_prestataire' in request.POST:
            prestataire_id = request.POST.get('prestataire_id')
            prestataire = get_object_or_404(Supplier, id=prestataire_id)
            nom = prestataire.nom
            prestataire.delete()
            
            messages.success(request, f'Prestataire {nom} supprimé avec succès!')
            return redirect('maintenance:configuration')
    
    # Récupération des données
    equipements = Equipement.objects.all().order_by('nom')
    prestataires = Supplier.objects.all().order_by('name')
    
    # Pagination des équipements
    equipements_paginator = Paginator(equipements, 5)  # 5 enregistrements par page
    equipements_page = request.GET.get('equipements_page', 1)
    equipements_page_obj = equipements_paginator.get_page(equipements_page)
    
    # Pagination des prestataires
    prestataires_paginator = Paginator(prestataires, 5)  # 5 enregistrements par page
    prestataires_page = request.GET.get('prestataires_page', 1)
    prestataires_page_obj = prestataires_paginator.get_page(prestataires_page)
    
    context = {
        'equipements': equipements_page_obj,
        'prestataires': prestataires_page_obj,
        'equipements_paginated': equipements_page_obj.has_other_pages(),
        'equipements_page_obj': equipements_page_obj,
        'prestataires_paginated': prestataires_page_obj.has_other_pages(),
        'prestataires_page_obj': prestataires_page_obj,
        'tab': tab,
    }
    
    return render(request, 'config.html', context)