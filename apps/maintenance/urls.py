from django.urls import path
from .views import (
    ConfigurationView, 
    ConventionListView, ConventionCreateView,
    ConventionUpdateView, ConventionDetailView, ConventionDeleteView,
    IncidentCreateView, IncidentListView, IncidentUpdateView, IncidentDeleteView, 
    InterventionListView, 
    StatisticsView,
    VisiteurCreateView, VisiteurListView,
    configuration
)

app_name = 'maintenance'

urlpatterns = [
    # Page d'accueil - Redirection vers les statistiques
    path('', StatisticsView.as_view(), name='Accueil'), 
    
    # Conventions
    path('conventions/', ConventionListView.as_view(), name='convention_list'),
    path('conventions/ajouter/', ConventionCreateView.as_view(), name='convention_add'),
    path('conventions/<int:pk>/', ConventionDetailView.as_view(), name='convention_detail'),
    path('conventions/<int:pk>/modifier/', ConventionUpdateView.as_view(), name='convention_edit'),
    path('conventions/<int:pk>/supprimer/', ConventionDeleteView.as_view(), name='convention_delete'),
    
    # Visiteurs
    path('visiteurs/', VisiteurListView.as_view(), name='visiteur_list'),
    path('visiteurs/ajouter/', VisiteurCreateView.as_view(), name='visiteur_add'),
    
    # Incidents
    path('incidents/', IncidentListView.as_view(), name='incident_list'),
    path('incidents/ajouter/', IncidentCreateView.as_view(), name='incident_add'),
    path('incidents/<int:pk>/modifier/', IncidentUpdateView.as_view(), name='incident_edit'),
    path('incidents/<int:pk>/supprimer/', IncidentDeleteView.as_view(), name='incident_delete'),

    # Interventions
    path('interventions/', InterventionListView.as_view(), name='intervention_list'),

    # Configuration
    path('configuration/', configuration, name='configuration'),

    # Statistiques
    path('statistiques/', StatisticsView.as_view(), name='statistiques'),
]