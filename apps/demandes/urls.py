from django.urls import path
from .views import configuration_demandes,demandes_internes,demandes_patients,statistiques_demandes_view,demande_stats_api,status_stats_api

app_name = 'demandes'

urlpatterns = [
    path('', statistiques_demandes_view, name='statistiques_demandes'), 
    path('configuration', configuration_demandes, name='configuration_demandes'),
    path('intern', demandes_internes, name='demandes_internes'),
    path('patient', demandes_patients, name='demandes_patients'),
    path('statistiques', statistiques_demandes_view, name='statistiques_demandes'),
    path('api/demande-stats/', demande_stats_api, name='demande_stats_api'),
    path('api/status-stats/', status_stats_api, name='status_stats_api'),
]