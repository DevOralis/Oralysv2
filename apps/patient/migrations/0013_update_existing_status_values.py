from django.db import migrations

def update_existing_status_values(apps, schema_editor):
    """Met à jour les statuts existants : 'sent' devient 'pending'"""
    BillingHistory = apps.get_model('patient', 'BillingHistory')
    
    # Mettre à jour tous les statuts 'sent' vers 'pending'
    BillingHistory.objects.filter(status='sent').update(status='pending')

def reverse_update_status_values(apps, schema_editor):
    """Fonction inverse : 'pending' redevient 'sent'"""
    BillingHistory = apps.get_model('patient', 'BillingHistory')
    
    # Remettre les statuts 'pending' vers 'sent' (pour rollback)
    BillingHistory.objects.filter(status='pending').update(status='sent')

class Migration(migrations.Migration):
    dependencies = [
        ('patient', '0012_update_status_choices'),
    ]
    
    operations = [
        migrations.RunPython(update_existing_status_values, reverse_update_status_values),
    ]



