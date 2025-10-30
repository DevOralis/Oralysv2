# Generated migration to populate invoice numbers for existing billing history

from django.db import migrations
import datetime


def generate_invoice_numbers(apps, schema_editor):
    """Génère des numéros de facture pour les enregistrements existants"""
    BillingHistory = apps.get_model('patient', 'BillingHistory')
    
    # Récupérer tous les enregistrements sans numéro de facture
    billing_records = BillingHistory.objects.filter(invoice_number__isnull=True)
    
    for record in billing_records:
        # Générer un numéro de facture basé sur la date de génération
        if record.generated_at:
            date = record.generated_at.date()
        else:
            date = datetime.date.today()
        
        # Compter les factures du même jour pour éviter les doublons
        count = BillingHistory.objects.filter(
            generated_at__date=date
        ).exclude(invoice_number__isnull=True).count() + 1
        
        # Générer le numéro unique
        invoice_number = f"FAC{date.strftime('%Y%m%d')}{count:03d}"
        
        # Vérifier l'unicité et incrémenter si nécessaire
        while BillingHistory.objects.filter(invoice_number=invoice_number).exists():
            count += 1
            invoice_number = f"FAC{date.strftime('%Y%m%d')}{count:03d}"
        
        # Sauvegarder
        record.invoice_number = invoice_number
        record.save()


def reverse_func(apps, schema_editor):
    """Fonction inverse - ne fait rien car on ne peut pas "dé-générer" les numéros"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0007_alter_billinghistory_invoice_number'),
    ]

    operations = [
        migrations.RunPython(generate_invoice_numbers, reverse_func),
    ]


