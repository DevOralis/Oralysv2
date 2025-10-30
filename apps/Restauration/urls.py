from django.urls import path
from .views import (
    restauration_home, menu_standard_list, menu_standard_create, menu_standard_update, menu_standard_delete,
    programme_list, programme_create, programme_update, programme_delete, programme_detail,
    programme_generate_weeks, programme_configure_menus_sequential, menu_personnalise_list, menu_personnalise_update, 
    menu_personnalise_delete, dashboard_restauration, api_programmes_mois,menu_supplementaire_create,
    menu_supplementaire_list, menu_supplementaire_update, menu_supplementaire_delete, menu_supplementaire_get_data,
    menu_supplementaire_update_ajax, client_suggestions, interventions_list, suivi_consommation_clients,
    restauration_config
)

urlpatterns = [
    # Dashboard principal
    path('', dashboard_restauration, name='dashboard_restauration'),
    
    # Gestion des plats et recettes
    path('plats/', restauration_home, name='restauration_home'),
    
    # Configuration des ingrédients et catégories
    path('configuration/', restauration_config, name='restauration_config'),
    
    # Gestion des menus standards
    path('menus-standards/', menu_standard_list, name='menu_standard_list'),
    path('menus-standards/nouveau/', menu_standard_create, name='menu_standard_create'),
    path('menus-standards/<int:pk>/modifier/', menu_standard_update, name='menu_standard_update'),
    path('menus-standards/<int:pk>/supprimer/', menu_standard_delete, name='menu_standard_delete'),
    
    # Gestion des programmes
    path('programmes/', programme_list, name='programme_list'),
    path('programmes/nouveau/', programme_create, name='programme_create'),
    path('programmes/<int:pk>/', programme_detail, name='programme_detail'),
    path('programmes/<int:pk>/modifier/', programme_update, name='programme_update'),
    path('programmes/<int:pk>/supprimer/', programme_delete, name='programme_delete'),
    path('programmes/<int:pk>/generer-semaines/', programme_generate_weeks, name='programme_generate_weeks'),
    path('programmes/<int:pk>/configurer-menus/', programme_configure_menus_sequential, name='programme_configure_menus_sequential'),
    path('programmes/<int:pk>/configurer-menus/<int:jour_id>/', programme_configure_menus_sequential, name='programme_configure_menus_sequential_with_jour'),
    

    # Gestion des menus personnalisés
    path('menus-personnalises/', menu_personnalise_list, name='menu_personnalise_list'),
    path('menus-personnalises/<int:pk>/modifier/', menu_personnalise_update, name='menu_personnalise_update'),
    path('menus-personnalises/<int:pk>/supprimer/', menu_personnalise_delete, name='menu_personnalise_delete'),
    
    # Gestion des menus supplémentaires
    path('menus-supplementaires/', menu_supplementaire_list, name='menu_supplementaire_list'),
    path('menus-supplementaires/nouveau/', menu_supplementaire_create, name='menu_supplementaire_create'),
    path('menus-supplementaires/<int:pk>/modifier/', menu_supplementaire_update, name='menu_supplementaire_update'),
    path('menus-supplementaires/<int:pk>/supprimer/', menu_supplementaire_delete, name='menu_supplementaire_delete'),
    # URLs AJAX pour modification en modal
    path('menus-supplementaires/<int:pk>/get-data/', menu_supplementaire_get_data, name='menu_supplementaire_get_data'),
    path('menus-supplementaires/<int:pk>/update-ajax/', menu_supplementaire_update_ajax, name='menu_supplementaire_update_ajax'),
    
    
    path('api/programmes-mois/', api_programmes_mois, name='api_programmes_mois'),
    
    # Demandes d'intervention
    #path('demande-intervention/', demande_intervention, name='demande_intervention'),
    #path('interventions/', interventions_list, name='interventions_list'),
    
    # API pour suggestions de clients
    path('api/client-suggestions/', client_suggestions, name='client_suggestions'),
    
    # Suivi Consommation Clients
    path('suivi-consommation-clients/', suivi_consommation_clients, name='suivi_consommation_clients'),
]