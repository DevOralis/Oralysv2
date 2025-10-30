from django.urls import path
from apps.home.views import (
    login_view, welcome_view, UserListView, UserToggleActivationView,
    UserDeleteView, user_table_body, logout_view, user_get, UserUpdateView,
    UserResetPasswordView, AuditLogListView, audit_log_table_body, audit_log_export_pdf,
    essential_components_view, unauthorized,user_management_dashboard,users_evolution_api,logs_by_action_api,
    users_activity_api, users_filtered_api, logs_filtered_api
)

urlpatterns = [
    path('', login_view, name='login_root'),
    path('unauthorized/', unauthorized, name='unauthorized'),
    path('login/', login_view, name='login'),
    path('welcome/', welcome_view, name='welcome'),
    path('logout/', logout_view, name='logout'),
    path('home/users/', UserListView.as_view(), name='user_list'),
    path('users/create/', UserListView.as_view(), name='user_create'),
    path('users/<int:pk>/get/', user_get, name='user_get'),
    path('users/<int:pk>/update/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/toggle-activation/', UserToggleActivationView.as_view(), name='user_toggle_activation'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('users/ajax/', user_table_body, name='user_table_body'),
    path('users/<int:pk>/reset-password/', UserResetPasswordView.as_view(), name='user_reset_password'),
    path('audit-logs/', AuditLogListView.as_view(), name='audit_log_list'),
    path('audit-logs/ajax/', audit_log_table_body, name='audit_log_table_body'),
    path('audit-logs/export-pdf/', audit_log_export_pdf, name='audit_log_export_pdf'),
    path('essential/', essential_components_view, name='essential_components'),
    path('users/dashboard/', user_management_dashboard, name='user_management_dashboard'),
    path('users_evolution_api/', users_evolution_api, name='users_evolution_api'),
    path('logs_by_action_api/', logs_by_action_api, name='logs_by_action_api'),
    path('users_activity_api/', users_activity_api, name='users_activity_api'),
    path('users_filtered_api/', users_filtered_api, name='users_filtered_api'),
    path('logs_filtered_api/', logs_filtered_api, name='logs_filtered_api'),
]