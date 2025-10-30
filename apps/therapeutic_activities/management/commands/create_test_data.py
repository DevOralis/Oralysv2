from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, time
from apps.hr.models.employee import Employee, Position
from apps.patient.models import Patient
from apps.therapeutic_activities.models import (
    ActivityType, ActivityLocation, Activity, Session, Participation
)


class Command(BaseCommand):
    help = 'Créer des données de test pour le module therapeutic_activities'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Création des données de test...'))

        # Créer les positions
        coach_position, created = Position.objects.get_or_create(
            name='Coach',
            defaults={'description': 'Coach d\'activités thérapeutiques'}
        )
        if created:
            self.stdout.write(f'✓ Position "{coach_position.name}" créée')
        else:
            self.stdout.write(f'✓ Position "{coach_position.name}" existe déjà')

        ergo_position, created = Position.objects.get_or_create(
            name='Ergothérapeute',
            defaults={'description': 'Ergothérapeute spécialisé'}
        )
        if created:
            self.stdout.write(f'✓ Position "{ergo_position.name}" créée')
        else:
            self.stdout.write(f'✓ Position "{ergo_position.name}" existe déjà')

        # Créer les employés
        coach1, created = Employee.objects.get_or_create(
            full_name='John Doe',
            defaults={
                'employee_id': 'COACH001',
                'national_id': 'EE123456',
                'birth_date': date(1985, 5, 15),
                'marital_status': 'M',
                'gender': 'M',
                'email': 'john.doe@example.com',
                'personal_phone': '0612345678',
                'work_phone': '0612345678',
                'personal_address': '123 Rue de la Paix, Paris',
                'work_address': 'Centre médical, Paris',
                'children_count': 0,
                'status': 'A',
                'position': coach_position,
                'base_salary': 3000.00,
                'career_evolution': 'Coach senior',
                'skills': 'Kinésithérapie, Rééducation'
            }
        )
        if created:
            self.stdout.write(f'✓ Coach "{coach1.full_name}" créé')
        else:
            self.stdout.write(f'✓ Coach "{coach1.full_name}" existe déjà')

        coach2, created = Employee.objects.get_or_create(
            full_name='Marie Martin',
            defaults={
                'employee_id': 'COACH002',
                'national_id': 'EE123457',
                'birth_date': date(1990, 8, 22),
                'marital_status': 'S',
                'gender': 'F',
                'email': 'marie.martin@example.com',
                'personal_phone': '0612345679',
                'work_phone': '0612345679',
                'personal_address': '456 Avenue des Champs, Lyon',
                'work_address': 'Centre médical, Lyon',
                'children_count': 0,
                'status': 'A',
                'position': coach_position,
                'base_salary': 2800.00,
                'career_evolution': 'Coach spécialisée',
                'skills': 'Art-thérapie, Musicothérapie'
            }
        )
        if created:
            self.stdout.write(f'✓ Coach "{coach2.full_name}" créé')
        else:
            self.stdout.write(f'✓ Coach "{coach2.full_name}" existe déjà')

        ergo1, created = Employee.objects.get_or_create(
            full_name='Sophie Dubois',
            defaults={
                'employee_id': 'ERGO001',
                'national_id': 'EE123458',
                'birth_date': date(1988, 3, 10),
                'marital_status': 'M',
                'gender': 'F',
                'email': 'sophie.dubois@example.com',
                'personal_phone': '0612345680',
                'work_phone': '0612345680',
                'personal_address': '789 Boulevard Central, Marseille',
                'work_address': 'Centre médical, Marseille',
                'children_count': 1,
                'status': 'A',
                'position': ergo_position,
                'base_salary': 3200.00,
                'career_evolution': 'Ergothérapeute senior',
                'skills': 'Ergothérapie, Réadaptation'
            }
        )
        if created:
            self.stdout.write(f'✓ Ergothérapeute "{ergo1.full_name}" créé')
        else:
            self.stdout.write(f'✓ Ergothérapeute "{ergo1.full_name}" existe déjà')

        # Créer les patients
        patients_data = [
            {'first_name': 'Jean', 'last_name': 'Dupont', 'full_name': 'Jean Dupont'},
            {'first_name': 'Marie', 'last_name': 'Durand', 'full_name': 'Marie Durand'},
            {'first_name': 'Pierre', 'last_name': 'Martin', 'full_name': 'Pierre Martin'},
            {'first_name': 'Sophie', 'last_name': 'Bernard', 'full_name': 'Sophie Bernard'},
            {'first_name': 'Lucas', 'last_name': 'Petit', 'full_name': 'Lucas Petit'},
        ]

        for patient_data in patients_data:
            patient, created = Patient.objects.get_or_create(
                full_name=patient_data['full_name'],
                defaults=patient_data
            )
            if created:
                self.stdout.write(f'✓ Patient "{patient.full_name}" créé')
            else:
                self.stdout.write(f'✓ Patient "{patient.full_name}" existe déjà')

        # Créer les types d'activités
        activity_types_data = [
            {'name': 'Thérapie physique', 'description': 'Activités de rééducation physique'},
            {'name': 'Ergothérapie', 'description': 'Activités d\'ergothérapie'},
            {'name': 'Art-thérapie', 'description': 'Activités artistiques thérapeutiques'},
            {'name': 'Musicothérapie', 'description': 'Activités musicales thérapeutiques'},
            {'name': 'Sport adapté', 'description': 'Activités sportives adaptées'},
        ]

        for type_data in activity_types_data:
            activity_type, created = ActivityType.objects.get_or_create(
                name=type_data['name'],
                defaults=type_data
            )
            if created:
                self.stdout.write(f'✓ Type d\'activité "{activity_type.name}" créé')
            else:
                self.stdout.write(f'✓ Type d\'activité "{activity_type.name}" existe déjà')

        # Créer les salles
        locations_data = [
            {'name': 'Salle de thérapie A', 'address': 'Bâtiment A, 1er étage', 'capacity': 10},
            {'name': 'Salle de thérapie B', 'address': 'Bâtiment A, 2ème étage', 'capacity': 8},
            {'name': 'Salle d\'ergothérapie', 'address': 'Bâtiment B, 1er étage', 'capacity': 6},
            {'name': 'Salle d\'art-thérapie', 'address': 'Bâtiment B, 2ème étage', 'capacity': 12},
            {'name': 'Gymnase', 'address': 'Bâtiment C, rez-de-chaussée', 'capacity': 20},
        ]

        for location_data in locations_data:
            location, created = ActivityLocation.objects.get_or_create(
                name=location_data['name'],
                defaults=location_data
            )
            if created:
                self.stdout.write(f'✓ Salle "{location.name}" créée')
            else:
                self.stdout.write(f'✓ Salle "{location.name}" existe déjà')

        # Créer les activités
        activities_data = [
            {
                'title': 'Séance de kinésithérapie',
                'description': 'Séance de rééducation physique',
                'type': ActivityType.objects.get(name='Thérapie physique'),
                'coach': coach1
            },
            {
                'title': 'Séance d\'ergothérapie',
                'description': 'Séance d\'ergothérapie spécialisée',
                'type': ActivityType.objects.get(name='Ergothérapie'),
                'coach': ergo1
            },
            {
                'title': 'Atelier peinture',
                'description': 'Atelier d\'art-thérapie par la peinture',
                'type': ActivityType.objects.get(name='Art-thérapie'),
                'coach': coach2
            },
            {
                'title': 'Séance de musicothérapie',
                'description': 'Séance de musicothérapie',
                'type': ActivityType.objects.get(name='Musicothérapie'),
                'coach': coach1
            },
            {
                'title': 'Gym douce',
                'description': 'Séance de gymnastique douce adaptée',
                'type': ActivityType.objects.get(name='Sport adapté'),
                'coach': coach2
            },
        ]

        for activity_data in activities_data:
            activity, created = Activity.objects.get_or_create(
                title=activity_data['title'],
                defaults=activity_data
            )
            if created:
                self.stdout.write(f'✓ Activité "{activity.title}" créée')
            else:
                self.stdout.write(f'✓ Activité "{activity.title}" existe déjà')

        # Créer quelques sessions
        sessions_data = [
            {
                'activity': Activity.objects.get(title='Séance de kinésithérapie'),
                'location': ActivityLocation.objects.get(name='Salle de thérapie A'),
                'date': date.today(),
                'start_time': time(9, 0),
                'end_time': time(10, 0),
                'max_participants': 5,
                'status': 'planned'
            },
            {
                'activity': Activity.objects.get(title='Séance d\'ergothérapie'),
                'location': ActivityLocation.objects.get(name='Salle d\'ergothérapie'),
                'date': date.today(),
                'start_time': time(10, 30),
                'end_time': time(11, 30),
                'max_participants': 3,
                'status': 'planned'
            },
            {
                'activity': Activity.objects.get(title='Atelier peinture'),
                'location': ActivityLocation.objects.get(name='Salle d\'art-thérapie'),
                'date': date.today(),
                'start_time': time(14, 0),
                'end_time': time(15, 30),
                'max_participants': 8,
                'status': 'planned'
            },
        ]

        for session_data in sessions_data:
            session, created = Session.objects.get_or_create(
                activity=session_data['activity'],
                date=session_data['date'],
                start_time=session_data['start_time'],
                defaults=session_data
            )
            if created:
                self.stdout.write(f'✓ Session "{session.activity.title}" créée')
            else:
                self.stdout.write(f'✓ Session "{session.activity.title}" existe déjà')

        # Créer quelques participations
        participations_data = [
            {
                'patient': Patient.objects.get(full_name='Jean Dupont'),
                'session': Session.objects.get(activity__title='Séance de kinésithérapie'),
                'status': 'present',
                'notes': 'Patient motivé'
            },
            {
                'patient': Patient.objects.get(full_name='Marie Durand'),
                'session': Session.objects.get(activity__title='Séance de kinésithérapie'),
                'status': 'present',
                'notes': 'Bonne participation'
            },
            {
                'patient': Patient.objects.get(full_name='Pierre Martin'),
                'session': Session.objects.get(activity__title='Séance d\'ergothérapie'),
                'status': 'present',
                'notes': 'Progrès notables'
            },
            {
                'patient': Patient.objects.get(full_name='Sophie Bernard'),
                'session': Session.objects.get(activity__title='Atelier peinture'),
                'status': 'present',
                'notes': 'Très créative'
            },
        ]

        for participation_data in participations_data:
            participation, created = Participation.objects.get_or_create(
                patient=participation_data['patient'],
                session=participation_data['session'],
                defaults=participation_data
            )
            if created:
                self.stdout.write(f'✓ Participation "{participation.patient.full_name}" créée')
            else:
                self.stdout.write(f'✓ Participation "{participation.patient.full_name}" existe déjà')

        self.stdout.write(self.style.SUCCESS('✓ Données de test créées avec succès !'))
        self.stdout.write(self.style.SUCCESS('Vous pouvez maintenant tester le module à l\'adresse :'))
        self.stdout.write(self.style.SUCCESS('http://localhost:8000/therapeutic_activities/activities_home/')) 