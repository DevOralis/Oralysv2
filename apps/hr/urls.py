# apps/hr/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Main HR URL
    path('', views.hr, name='human_resources'),
    # Dashboard HR
    path('statistics/', views.hr_statistics, name='hr_statistics'),
    # Configuration
    path('configuration/', views.hr_configuration, name='hr_configuration'),
    # CRUD URLs for each entity
    path('position/crud/', views.handle_position_crud, name='handle_position_crud'),
    path('department/crud/', views.handle_department_crud, name='handle_department_crud'),
    path('contract-type/crud/', views.handle_contract_type_crud, name='handle_contract_type_crud'),
    path('prime/crud/', views.handle_prime_crud, name='handle_prime_crud'),
    path('model-calcul/crud/', views.handle_model_calcul_crud, name='handle_model_calcul_crud'),
    # Employee Management
    path('employees/', views.liste_employes, name='liste_employes'),
    path('employees/add/', views.add_employee, name='add_employee'),
    path('employees/delete/', views.supprimer_employe, name='supprimer_employe'),
    path('employees/data/<int:employe_id>/', views.get_employe_data, name='get_employe_data'),
    path('employee/<int:employee_id>/details/', views.employee_details, name='employee_details'),
    
    # Leave Management
    path('leaves/', views.gestion_conges, name='gestion_conges'),
    path('leaves/approval/', views.approbation_conges, name='approbation_conges'),
    path('leaves/manager-approval/', views.manager_approval_conges, name='manager_approval_conges'),
    path('leaves/calendar/', views.calendar_conges, name='calendar_conges'),
    path('leaves/submit/', views.submit_leave_request, name='submit_leave_request'),
    # URL alternative pour éviter l'erreur 404 (utilisée par certains templates)
    path('submit_leave_request/', views.submit_leave_request, name='submit_leave_request_alt'),
    path('leave-request-details/<int:request_id>/', views.get_leave_request_details, name='get_leave_request_details'),
    path('leave-request-approve/<int:request_id>/', views.approve_leave_request, name='approve_leave_request'),
    path('leave-request-refuse/<int:request_id>/', views.refuse_leave_request, name='refuse_leave_request'),
    path('leave-request-manager-decision/<int:request_id>/', views.manager_decision_leave_request, name='manager_decision_leave_request'),
    path('leaves/cancel/<int:request_id>/', views.cancel_leave_request, name='cancel_leave_request'),
    path('leaves/get/<int:request_id>/', views.get_leave_request, name='get_leave_request'),
    path('leaves/edit/<int:request_id>/', views.edit_leave_request, name='edit_leave_request'),
    path('leaves/submit/<int:request_id>/', views.submit_draft_request, name='submit_draft_request'),
    path('leaves/delete/<int:request_id>/', views.delete_leave_request, name='delete_leave_request'),
    path('leaves/type/crud/', views.handle_leave_type_crud, name='handle_leave_type_crud'),
    path('calendar/', views.calendar_conges, name='calendar_conges'),
    path('leaves/get_calendar_events/', views.get_calendar_events, name='get_calendar_events'),
    
]

urlpatterns += [
    path('payroll/', views.payroll_management, name='payroll_management'),
    path('payroll/download/', views.download_payroll_pdf, name='download_payroll_pdf'),
    path('payroll/history/', views.payroll_history, name='payroll_history'),
    path('social-contributions/', views.social_contribution_list, name='social_contribution_list'),
    path('social-contributions/create/', views.social_contribution_create, name='social_contribution_create'),
    path('social-contributions/update/<int:pk>/', views.social_contribution_update, name='social_contribution_update'),
    path('social-contributions/delete/<int:pk>/', views.social_contribution_delete, name='social_contribution_delete'),
    path('social-contributions/crud/', views.handle_social_contribution_crud, name='handle_social_contribution_crud'),
    # Gestion CRUD pour la configuration (spécialités, etc.)
    path('configuration/crud/', views.handle_speciality_crud, name='handle_speciality_crud'),
] 

# URLs pour la gestion des sorties
from . import views
urlpatterns += [
    path('sorties/', views.gestion_sorties, name='gestion_sorties'),
    path('sorties/ajouter/', views.ajouter_sortie, name='ajouter_sortie'),
    path('sorties/supprimer/<int:sortie_id>/', views.supprimer_sortie, name='supprimer_sortie'),
    path('sorties/modifier/<int:sortie_id>/', views.modifier_sortie, name='modifier_sortie'),
]