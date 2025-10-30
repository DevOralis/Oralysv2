from django.contrib.contenttypes.models import ContentType
from .models import AuditLog

def log_action(user, instance, action):
    """
    Enregistre une action dans le journal d'audit.
    
    Args:
        user: Utilisateur connecté (instance de User)
        instance: Instance de l'objet concerné (ex: Supplier, PurchaseOrder)
        action: Type d'action ('creation', 'modification', 'suppression', 'impression')
    """
    if not user or not user.is_authenticated:
        return  # Ne rien faire si pas d'utilisateur connecté

    content_type = ContentType.objects.get_for_model(instance)
    entity_name = instance.__class__.__name__
    
    AuditLog.objects.create(
        created_by=user,
        entity_name=entity_name,
        object_id=str(instance.pk),
        content_type=content_type,
        action=action
    )