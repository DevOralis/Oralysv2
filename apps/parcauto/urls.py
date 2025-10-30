# urls.py
from django.urls import path
from .views import (
    parcauto_home, configuration_list, get_modeles_by_marque, entretien, 
    affectation, contract, entretien_events, statistics, get_model_data_ajax,
    get_expiring_contracts_count, marque_create, marque_update, marque_delete,
    modele_create, modele_update, modele_delete, contract_type_create, 
    contract_type_update, contract_type_delete, provider_create, provider_update, 
    provider_delete, entretien_type_create, entretien_type_update, entretien_type_delete
)

urlpatterns = [
    path('', parcauto_home, name='parcauto_home'),
    path('configuration/', configuration_list, name='parcauto_configuration'),
    path('entretien', entretien, name='entretien'),
    path('affectation/', affectation, name='affectation'),
    path('contract/', contract, name='contract'),
    path('statistics/', statistics, name='parcauto_statistics'),
    path('model-data/<int:model_id>/', get_model_data_ajax, name='get_model_data_ajax'),
    path('get_modeles/<int:marque_id>/', get_modeles_by_marque, name='get_modeles_by_marque'),
    path('entretien/events/', entretien_events, name='entretien_events'),
        path('api/contracts/expiring-count/', get_expiring_contracts_count, name='expiring_contracts_count'),

    # Marque URLs
    path('configuration/marque/create/', marque_create, name='marque_create'),
    path('configuration/marque/<int:marque_id>/update/', marque_update, name='marque_update'),
    path('configuration/marque/<int:marque_id>/delete/', marque_delete, name='marque_delete'),

    # Modele URLs
    path('configuration/modele/create/', modele_create, name='modele_create'),
    path('configuration/modele/<int:modele_id>/update/', modele_update, name='modele_update'),
    path('configuration/modele/<int:modele_id>/delete/', modele_delete, name='modele_delete'),

    # Contract Type URLs
    path('configuration/contract-type/create/', contract_type_create, name='contract_type_create'),
    path('configuration/contract-type/<int:type_id>/update/', contract_type_update, name='contract_type_update'),
    path('configuration/contract-type/<int:type_id>/delete/', contract_type_delete, name='contract_type_delete'),

    # Provider URLs
    path('configuration/provider/create/', provider_create, name='provider_create'),
    path('configuration/provider/<int:provider_id>/update/', provider_update, name='provider_update'),
    path('configuration/provider/<int:provider_id>/delete/', provider_delete, name='provider_delete'),

    # Entretien Type URLs
    path('configuration/entretien-type/create/', entretien_type_create, name='entretien_type_create'),
    path('configuration/entretien-type/<int:type_id>/update/', entretien_type_update, name='entretien_type_update'),
    path('configuration/entretien-type/<int:type_id>/delete/', entretien_type_delete, name='entretien_type_delete'),
]