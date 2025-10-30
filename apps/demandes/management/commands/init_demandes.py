from django.core.management.base import BaseCommand
from apps.demandes.models import Priorite, Statut, Department

class Command(BaseCommand):
    help = 'Initialise les données de base pour le module demandes'

    def handle(self, *args, **options):
        # Créer les priorités de base
        priorites = [
            {'nom': 'Basse', 'niveau': 1},
            {'nom': 'Normale', 'niveau': 2},
            {'nom': 'Haute', 'niveau': 3},
            {'nom': 'Urgente', 'niveau': 4},
        ]
        
        for p in priorites:
            Priorite.objects.get_or_create(nom=p['nom'], defaults={'niveau': p['niveau']})
        
        # Créer les statuts de base
        statuts = [
            {'nom': 'Nouvelle', 'couleur': 'info', 'category': 'active'},
            {'nom': 'En cours', 'couleur': 'warning', 'category': 'active'},
            {'nom': 'Terminée', 'couleur': 'success', 'category': 'terminated'},
            {'nom': 'Annulée', 'couleur': 'danger', 'category': 'cancelled'},
        ]
        
        for s in statuts:
            Statut.objects.get_or_create(nom=s['nom'], defaults=s)
        
        # Créer quelques départements de base
        departements = [
            'Administration',
            'Maintenance',
            'Restauration',
            'Médical',
            'Logistique',
        ]
        
        for d in departements:
            Department.objects.get_or_create(name=d)
        
        self.stdout.write(
            self.style.SUCCESS('Données de base créées avec succès pour le module demandes')
        )

