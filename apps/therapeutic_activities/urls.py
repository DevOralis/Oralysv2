from django.urls import path
from . import views

app_name = "therapeutic_activities"

urlpatterns = [
    # ========================================
    # PAGES D'ACCUEIL
    # ========================================
    path('', views.activities_home, name='activities_home'),
    path('activities_home/', views.activities_home, name='activities_home_alt'),
    
    # ========================================
    # CONFIGURATION
    # ========================================
    path('configuration/', views.configuration, name='configuration'),
    
    # ========================================
    # ACTIVITÉS
    # ========================================
    path('activities/', views.activity_list, name='activity_list'),
    path('activities/create/', views.activity_create, name='activity_create'),
    path('activities/<int:pk>/edit/', views.activity_edit, name='activity_edit'),
    path('activities/<int:pk>/delete/', views.activity_delete, name='activity_delete'),
    path('activities/<int:pk>/preview/', views.activity_preview, name='activity_preview'),
    
    # ========================================
    # SESSIONS
    # ========================================
    path('sessions/', views.session_list, name='session_list'),
    path('sessions/create/', views.session_create, name='session_create'),
    path('sessions/<int:pk>/edit/', views.session_edit, name='session_edit'),
    path('sessions/<int:pk>/delete/', views.session_delete, name='session_delete'),
    path('sessions/calendar/', views.session_calendar, name='session_calendar'),
    
    # ========================================
    # PARTICIPATIONS
    # ========================================
    path('participations/', views.participation_list, name='participation_list'),
    path('participations/create/', views.participation_create, name='participation_create'),
    path('participations/<int:pk>/edit/', views.participation_edit, name='participation_edit'),
    path('participations/<int:pk>/delete/', views.participation_delete, name='participation_delete'),
    path('participations/bulk-create/', views.bulk_participation_create, name='bulk_participation_create'),
    
    # ========================================
    # ÉVALUATIONS SPÉCIALISÉES
    # ========================================
    path('participations/<int:participation_pk>/ergotherapy-evaluation/', 
         views.ergotherapy_evaluation_create, name='ergotherapy_evaluation_create'),
    path('participations/<int:participation_pk>/ergotherapy-evaluation/detail/', 
         views.ergotherapy_evaluation_detail, name='ergotherapy_evaluation_detail'),
    path('participations/<int:participation_pk>/ergotherapy-evaluation/edit/', 
         views.ergotherapy_evaluation_edit, name='ergotherapy_evaluation_edit'),
    
    path('participations/<int:participation_pk>/coaching-session/', 
         views.coaching_session_create, name='coaching_session_create'),
    path('participations/<int:participation_pk>/coaching-session/detail/', 
         views.coaching_session_detail, name='coaching_session_detail'),
    path('participations/<int:participation_pk>/coaching-session/edit/', 
         views.coaching_session_edit, name='coaching_session_edit'),
    
    path('participations/<int:participation_pk>/social-report/', 
         views.social_report_create, name='social_report_create'),
    path('participations/<int:participation_pk>/social-report/detail/', 
         views.social_report_detail, name='social_report_detail'),
    path('participations/<int:participation_pk>/social-report/edit/', 
         views.social_report_edit, name='social_report_edit'),
    
    # ========================================
    # ÉVALUATIONS ERGOTHÉRAPIQUES - LISTES
    # ========================================
    path('ergotherapy-evaluations/', views.ergotherapy_evaluation_list, name='ergotherapy_evaluation_list'),
    path('ergotherapy-evaluations/create/', views.ergotherapy_evaluation_create_standalone, name='ergotherapy_evaluation_create_standalone'),
    path('coaching-sessions/', views.coaching_session_list, name='coaching_session_list'),
    path('coaching-sessions/create/', views.coaching_session_create_standalone, name='coaching_session_create_standalone'),
    path('social-reports/', views.social_report_list, name='social_report_list'),
    path('social-reports/create/', views.social_report_create_standalone, name='social_report_create_standalone'),
    
    # ========================================
    # STATISTIQUES ET RAPPORTS
    # ========================================
    path('statistics/', views.statistics_dashboard, name='statistics_dashboard'),
    path('patient/<int:patient_id>/follow-up/', views.patient_follow_up, name='patient_follow_up'),
    path('activity-type/<int:activity_type_id>/report/', views.activity_type_report, name='activity_type_report'),
    
    # ========================================
    # ALERTES
    # ========================================
    path('alerts/', views.alerts_dashboard, name='alerts_dashboard'),
    
    # ========================================
    # RECHERCHE AJAX
    # ========================================
    path('search/activity-types/', views.search_activity_types, name='search_activity_types'),
    path('search/activity-locations/', views.search_activity_locations, name='search_activity_locations'),
    
    # ========================================
    # CRUD AJAX
    # ========================================
    path('ajax/create-activity-type/', views.create_activity_type, name='create_activity_type'),
    path('ajax/create-activity-location/', views.create_activity_location, name='create_activity_location'),
    path('ajax/delete-activity-type/', views.delete_activity_type, name='delete_activity_type'),
    path('ajax/delete-activity-location/', views.delete_activity_location, name='delete_activity_location'),
    
    # ========================================
    # API ROUTES
    # ========================================
    # Activity Types API
    path('api/activity-types/create/', views.create_activity_type, name='api_create_activity_type'),
    path('api/activity-types/<int:pk>/update/', views.update_activity_type, name='api_update_activity_type'),
    path('api/activity-types/<int:pk>/delete/', views.delete_activity_type, name='api_delete_activity_type'),
    
    # Activity Locations API
    path('api/activity-locations/create/', views.create_activity_location, name='api_create_activity_location'),
    path('api/activity-locations/<int:pk>/update/', views.update_activity_location, name='api_update_activity_location'),
    path('api/activity-locations/<int:pk>/delete/', views.delete_activity_location, name='api_delete_activity_location'),
    
    # Sessions API
    path('api/sessions/', views.api_sessions, name='api_sessions'),
    path('api/activity-coaches/<int:activity_id>/', views.api_activity_coaches, name='api_activity_coaches'),
]
