from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('formation/', views.formation_stats_view, name='formation_stats'),
    path('demandes/', views.demandes_stats_view, name='demandes_stats'),
    path('purchases/', views.purchases_stats_view, name='purchases_stats'),
    path('hosting/', views.hosting_stats_view, name='hosting_stats'),
    path('inventory/', views.inventory_stats_view, name='inventory_stats'),
    path('maintenance/', views.maintenance_stats_view, name='maintenance_stats'),
    path('parcauto/', views.parcauto_stats_view, name='parcauto_stats'),
    path('pharmacy/', views.pharmacy_stats_view, name='pharmacy_stats'),
    path('recruitment/', views.recruitment_stats_view, name='recruitment_stats'),
    path('patient/', views.patient_stats_view, name='patient_stats'),
    path('restauration/', views.restauration_stats_view, name='restauration_stats'),
    path('hr/', views.hr_stats_view, name='hr_stats'),
    path('therapeutic-activities/', views.therapeutic_activities_stats_view, name='therapeutic_activities_stats'),
]

