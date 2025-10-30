from django import template
from django.urls import resolve, Resolver404
import logging

register = template.Library()
logger = logging.getLogger(__name__)

# Define app-to-URL mappings (same as in middleware and welcome_view)
apps_urls = {
    'reception': '/reception/',
    'consultation': '/patient/consultation/',
    'billing': '/billing/',
    'hospitalization': '/hospitalization/',
    'pharmacy': '/pharmacy/',
    'activities': '/activities/',
    'purchases': '/purchases/',
    'stock_moves': '/inventory/stock-moves/',
    'inventory': '/inventory/products/',
    'restaurant': '/restaurant/',
    'hr': '/hr/',
    'maintenance': '/maintenance/',
    'patient': '/patient/',
    'home': '/home/',
    'home.user_list': '/user/list/'
}

@register.simple_tag(takes_context=True)
def has_permission(context, permission_type):
    """
    Check if the user has the specified permission for the current app.
    permission_type can be 'read', 'write', 'update', or 'delete'.
    """
    request = context['request']
    if not request.session.get('user'):
        return False

    permissions = context.get('user_permissions', {})
    requested_path = request.path

    # Determine the current app based on the URL
    current_app = None
    for app_name, url in apps_urls.items():
        if requested_path.startswith(url):
            current_app = f"apps.{app_name}" if app_name != 'home.user_list' else 'apps.home'
            break

    if not current_app or current_app not in permissions:
        logger.warning(f"No permissions found for app {current_app} or path {requested_path}")
        return False

    return permissions[current_app].get(permission_type, False)