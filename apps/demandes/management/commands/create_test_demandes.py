from django.core.management.base import BaseCommand
from apps.demandes.models import Priorite, Statut, Department, DemandeInterne, DemandePatient, DemandePatientModel
from apps.purchases.models import Supplier

class Command(BaseCommand):
    help = 'Crée des demandes de test pour le module demandes'

    def handle(self, *args, **options):
        # Récupérer les objets existants
        priorite_normale = Priorite.objects.get(nom='Normale')
        statut_nouvelle = Statut.objects.get(nom='Nouvelle')
        statut_en_cours = Statut.objects.get(nom='En cours')
        dept_maintenance = Department.objects.get(name='Maintenance')
        dept_restauration = Department.objects.get(name='Restauration')
        
        # Créer un prestataire de test
        prestataire, created = Supplier.objects.get_or_create(
            nom='Tech Solutions SARL',
            defaults={'contact': 'Maintenance informatique', 'adresse': 'Casablanca, Maroc'}
        )
        
        # Créer un patient de test
        patient, created = DemandePatientModel.objects.get_or_create(
            nom='Dupont',
            prenom='Marie',
            defaults={'sexe': 'F', 'chambre': 'A101', 'telephone': '0612345678'}
        )
        
        # Créer des demandes internes de test
        demande1, created = DemandeInterne.objects.get_or_create(
            description='Maintenance préventive des serveurs',
            defaults={
                'priorite': priorite_normale,
                'statut': statut_nouvelle,
                'departement_source': dept_maintenance,
                'departement_destinataire': dept_maintenance,
                'prestataire': prestataire
            }
        )
        
        demande2, created = DemandeInterne.objects.get_or_create(
            description='Installation nouveau logiciel de gestion',
            defaults={
                'priorite': priorite_normale,
                'statut': statut_en_cours,
                'departement_source': dept_restauration,
                'departement_destinataire': dept_maintenance,
                'prestataire': prestataire
            }
        )
        
        # Créer une demande patient de test
        demande_patient, created = DemandePatient.objects.get_or_create(
            description='Demande de repas spécial sans gluten',
            defaults={
                'priorite': priorite_normale,
                'statut': statut_nouvelle,
                'patient': patient
            }
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Demandes de test créées avec succès: {DemandeInterne.objects.count()} internes, {DemandePatient.objects.count()} patients')
        )

