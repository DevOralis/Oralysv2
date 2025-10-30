from django.core.management.base import BaseCommand
from apps.hr.models.contract import Contract

class Command(BaseCommand):
    help = 'Supprime les contrats orphelins (avec employee_id=null)'

    def handle(self, *args, **options):
        # Trouver tous les contrats orphelins
        orphaned_contracts = Contract.objects.filter(employee_id__isnull=True)
        count = orphaned_contracts.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('Aucun contrat orphelin trouvé.')
            )
            return
        
        # Afficher les contrats qui seront supprimés
        self.stdout.write(f'Contrats orphelins trouvés ({count}):')
        for contract in orphaned_contracts:
            self.stdout.write(f'  - ID: {contract.id}, Type: {contract.contract_type}, Date: {contract.start_date}')
        
        # Demander confirmation
        confirm = input(f'Voulez-vous supprimer ces {count} contrats orphelins? (y/N): ')
        
        if confirm.lower() in ['y', 'yes', 'oui', 'o']:
            # Supprimer les contrats orphelins
            deleted_count = orphaned_contracts.delete()[0]
            self.stdout.write(
                self.style.SUCCESS(f'Supprimé avec succès {deleted_count} contrats orphelins.')
            )
        else:
            self.stdout.write('Opération annulée.')
