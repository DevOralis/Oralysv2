from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date, time
from apps.hr.models.employee import Employee, Position
from apps.patient.models import Patient
from .models import (
    ActivityType, ActivityLocation, Activity, Session, 
    Participation, ErgotherapyEvaluation, CoachingSession, SocialReport
)


class TherapeuticActivitiesTestCase(TestCase):
    """Classe de base pour les tests des activités thérapeutiques"""
    
    def setUp(self):
        """Configuration initiale pour tous les tests"""
        # Créer une position coach
        self.coach_position = Position.objects.create(name='Coach')
        
        # Créer un employé coach
        self.coach = Employee.objects.create(
            first_name='John',
            last_name='Doe',
            full_name='John Doe',
            position=self.coach_position
        )
        
        # Créer un patient
        self.patient = Patient.objects.create(
            first_name='Jane',
            last_name='Smith',
            full_name='Jane Smith'
        )
        
        # Créer des types d'activités
        self.activity_type = ActivityType.objects.create(
            name='Thérapie physique',
            description='Activités de rééducation physique'
        )
        
        # Créer une salle
        self.location = ActivityLocation.objects.create(
            name='Salle de thérapie',
            address='Bâtiment A, 1er étage',
            capacity=10
        )
        
        # Créer une activité
        self.activity = Activity.objects.create(
            title='Séance de kinésithérapie',
            description='Séance de rééducation',
            type=self.activity_type,
            coach=self.coach
        )
        
        # Créer une session
        self.session = Session.objects.create(
            activity=self.activity,
            location=self.location,
            date=date.today(),
            start_time=time(9, 0),
            end_time=time(10, 0),
            max_participants=5
        )
        
        # Créer une participation
        self.participation = Participation.objects.create(
            patient=self.patient,
            session=self.session,
            status='present'
        )


class ModelTests(TestCase):
    """Tests pour les modèles"""
    
    def setUp(self):
        self.coach_position = Position.objects.create(name='Coach')
        self.coach = Employee.objects.create(
            first_name='John', last_name='Doe', full_name='John Doe',
            position=self.coach_position
        )
        self.patient = Patient.objects.create(
            first_name='Jane', last_name='Smith', full_name='Jane Smith'
        )
        self.activity_type = ActivityType.objects.create(
            name='Thérapie physique', description='Activités de rééducation'
        )
        self.location = ActivityLocation.objects.create(
            name='Salle de thérapie', address='Bâtiment A', capacity=10
        )
        self.activity = Activity.objects.create(
            title='Kinésithérapie', description='Rééducation',
            type=self.activity_type, coach=self.coach
        )
        self.session = Session.objects.create(
            activity=self.activity, location=self.location,
            date=date.today(), start_time=time(9, 0), end_time=time(10, 0),
            max_participants=5
        )
        self.participation = Participation.objects.create(
            patient=self.patient, session=self.session, status='present'
        )

    def test_activity_type_str(self):
        """Test de la méthode __str__ pour ActivityType"""
        self.assertEqual(str(self.activity_type), 'Thérapie physique')

    def test_activity_location_str(self):
        """Test de la méthode __str__ pour ActivityLocation"""
        self.assertEqual(str(self.location), 'Salle de thérapie')

    def test_activity_str(self):
        """Test de la méthode __str__ pour Activity"""
        self.assertEqual(str(self.activity), 'Kinésithérapie')

    def test_session_str(self):
        """Test de la méthode __str__ pour Session"""
        expected = f"Session de {self.activity.title} le {self.session.date}"
        self.assertEqual(str(self.session), expected)

    def test_participation_str(self):
        """Test de la méthode __str__ pour Participation"""
        expected = f"{self.patient.full_name} - {self.session}"
        self.assertEqual(str(self.participation), expected)

    def test_activity_type_properties(self):
        """Test des propriétés calculées d'ActivityType"""
        self.assertEqual(self.activity_type.activities_count, 1)
        self.assertEqual(self.activity_type.sessions_count, 1)

    def test_session_properties(self):
        """Test des propriétés calculées de Session"""
        self.assertEqual(self.session.duration_minutes, 60)
        self.assertEqual(self.session.participants_count, 1)
        self.assertEqual(self.session.available_spots, 4)
        self.assertFalse(self.session.is_full)

    def test_participation_properties(self):
        """Test des propriétés calculées de Participation"""
        self.assertFalse(self.participation.has_evaluation)
        self.assertFalse(self.participation.has_coaching)
        self.assertFalse(self.participation.has_social_report)


class ViewTests(TestCase):
    """Tests pour les vues"""
    
    def setUp(self):
        self.client = Client()
        self.coach_position = Position.objects.create(name='Coach')
        self.coach = Employee.objects.create(
            first_name='John', last_name='Doe', full_name='John Doe',
            position=self.coach_position
        )
        self.patient = Patient.objects.create(
            first_name='Jane', last_name='Smith', full_name='Jane Smith'
        )
        self.activity_type = ActivityType.objects.create(
            name='Thérapie physique', description='Activités de rééducation'
        )
        self.location = ActivityLocation.objects.create(
            name='Salle de thérapie', address='Bâtiment A', capacity=10
        )
        self.activity = Activity.objects.create(
            title='Kinésithérapie', description='Rééducation',
            type=self.activity_type, coach=self.coach
        )
        self.session = Session.objects.create(
            activity=self.activity, location=self.location,
            date=date.today(), start_time=time(9, 0), end_time=time(10, 0),
            max_participants=5
        )
        self.participation = Participation.objects.create(
            patient=self.patient, session=self.session, status='present'
        )

    def test_activities_home_view(self):
        """Test de la vue d'accueil"""
        response = self.client.get(reverse('therapeutic_activities:activities_home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'activities_home.html')

    def test_activity_list_view(self):
        """Test de la vue liste des activités"""
        response = self.client.get(reverse('therapeutic_activities:activity_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'activity_list.html')
        self.assertContains(response, 'Kinésithérapie')

    def test_session_list_view(self):
        """Test de la vue liste des sessions"""
        response = self.client.get(reverse('therapeutic_activities:session_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'session_list.html')

    def test_participation_list_view(self):
        """Test de la vue liste des participations"""
        response = self.client.get(reverse('therapeutic_activities:participation_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'participation_list.html')

    def test_configuration_view(self):
        """Test de la vue configuration"""
        response = self.client.get(reverse('therapeutic_activities:configuration'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'configuration.html')

    def test_activity_create_view(self):
        """Test de la création d'activité"""
        data = {
            'title': 'Nouvelle activité',
            'description': 'Description test',
            'type': self.activity_type.id,
            'coach': self.coach.id,
            'is_active': True
        }
        response = self.client.post(reverse('therapeutic_activities:activity_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirection après création
        self.assertTrue(Activity.objects.filter(title='Nouvelle activité').exists())

    def test_session_create_view(self):
        """Test de la création de session"""
        data = {
            'activity': self.activity.id,
            'location': self.location.id,
            'date': date.today(),
            'start_time': '10:00',
            'end_time': '11:00',
            'max_participants': 5,
            'status': 'planned'
        }
        response = self.client.post(reverse('therapeutic_activities:session_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirection après création

    def test_participation_create_view(self):
        """Test de la création de participation"""
        data = {
            'patient': self.patient.id,
            'session': self.session.id,
            'status': 'present',
            'notes': 'Test participation'
        }
        response = self.client.post(reverse('therapeutic_activities:participation_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirection après création


class FormTests(TestCase):
    """Tests pour les formulaires"""
    
    def setUp(self):
        self.coach_position = Position.objects.create(name='Coach')
        self.coach = Employee.objects.create(
            first_name='John', last_name='Doe', full_name='John Doe',
            position=self.coach_position
        )
        self.patient = Patient.objects.create(
            first_name='Jane', last_name='Smith', full_name='Jane Smith'
        )
        self.activity_type = ActivityType.objects.create(
            name='Thérapie physique', description='Activités de rééducation'
        )
        self.location = ActivityLocation.objects.create(
            name='Salle de thérapie', address='Bâtiment A', capacity=10
        )
        self.activity = Activity.objects.create(
            title='Kinésithérapie', description='Rééducation',
            type=self.activity_type, coach=self.coach
        )
        self.session = Session.objects.create(
            activity=self.activity, location=self.location,
            date=date.today(), start_time=time(9, 0), end_time=time(10, 0),
            max_participants=5
        )

    def test_activity_type_form_valid(self):
        """Test du formulaire ActivityType avec données valides"""
        from .forms import ActivityTypeForm
        data = {
            'name': 'Nouveau type',
            'description': 'Description test',
            'is_active': True
        }
        form = ActivityTypeForm(data=data)
        self.assertTrue(form.is_valid())

    def test_activity_form_valid(self):
        """Test du formulaire Activity avec données valides"""
        from .forms import ActivityForm
        data = {
            'title': 'Nouvelle activité',
            'description': 'Description test',
            'type': self.activity_type.id,
            'coach': self.coach.id,
            'is_active': True
        }
        form = ActivityForm(data=data)
        self.assertTrue(form.is_valid())

    def test_session_form_valid(self):
        """Test du formulaire Session avec données valides"""
        from .forms import SessionForm
        data = {
            'activity': self.activity.id,
            'location': self.location.id,
            'date': date.today(),
            'start_time': '10:00',
            'end_time': '11:00',
            'max_participants': 5,
            'status': 'planned'
        }
        form = SessionForm(data=data)
        self.assertTrue(form.is_valid())

    def test_participation_form_valid(self):
        """Test du formulaire Participation avec données valides"""
        from .forms import ParticipationForm
        data = {
            'patient': self.patient.id,
            'session': self.session.id,
            'status': 'present',
            'notes': 'Test participation'
        }
        form = ParticipationForm(data=data)
        self.assertTrue(form.is_valid())


class IntegrationTests(TestCase):
    """Tests d'intégration pour les workflows complets"""
    
    def setUp(self):
        self.client = Client()
        self.coach_position = Position.objects.create(name='Coach')
        self.coach = Employee.objects.create(
            first_name='John', last_name='Doe', full_name='John Doe',
            position=self.coach_position
        )
        self.patient = Patient.objects.create(
            first_name='Jane', last_name='Smith', full_name='Jane Smith'
        )
        self.activity_type = ActivityType.objects.create(
            name='Thérapie physique', description='Activités de rééducation'
        )
        self.location = ActivityLocation.objects.create(
            name='Salle de thérapie', address='Bâtiment A', capacity=10
        )

    def test_complete_workflow(self):
        """Test d'un workflow complet : créer activité -> session -> participation"""
        # 1. Créer une activité
        activity_data = {
            'title': 'Test activité',
            'description': 'Description test',
            'type': self.activity_type.id,
            'coach': self.coach.id,
            'is_active': True
        }
        response = self.client.post(reverse('therapeutic_activities:activity_create'), activity_data)
        self.assertEqual(response.status_code, 302)
        
        activity = Activity.objects.get(title='Test activité')
        
        # 2. Créer une session
        session_data = {
            'activity': activity.id,
            'location': self.location.id,
            'date': date.today(),
            'start_time': '10:00',
            'end_time': '11:00',
            'max_participants': 5,
            'status': 'planned'
        }
        response = self.client.post(reverse('therapeutic_activities:session_create'), session_data)
        self.assertEqual(response.status_code, 302)
        
        session = Session.objects.get(activity=activity)
        
        # 3. Créer une participation
        participation_data = {
            'patient': self.patient.id,
            'session': session.id,
            'status': 'present',
            'notes': 'Test participation'
        }
        response = self.client.post(reverse('therapeutic_activities:participation_create'), participation_data)
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que tout a été créé
        self.assertTrue(Activity.objects.filter(title='Test activité').exists())
        self.assertTrue(Session.objects.filter(activity=activity).exists())
        self.assertTrue(Participation.objects.filter(session=session).exists())


class APITests(TestCase):
    """Tests pour les endpoints AJAX"""
    
    def setUp(self):
        self.client = Client()
        self.activity_type = ActivityType.objects.create(
            name='Thérapie physique', description='Activités de rééducation'
        )
        self.location = ActivityLocation.objects.create(
            name='Salle de thérapie', address='Bâtiment A', capacity=10
        )

    def test_search_activity_types(self):
        """Test de la recherche AJAX des types d'activités"""
        response = self.client.get(reverse('therapeutic_activities:search_activity_types'), {
            'q': 'physique'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('html', response.json())

    def test_search_activity_locations(self):
        """Test de la recherche AJAX des salles"""
        response = self.client.get(reverse('therapeutic_activities:search_activity_locations'), {
            'q': 'thérapie'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('html', response.json())

    def test_create_activity_type_ajax(self):
        """Test de la création AJAX d'un type d'activité"""
        data = {
            'name': 'Nouveau type AJAX',
            'description': 'Description AJAX',
            'is_active': True
        }
        response = self.client.post(reverse('therapeutic_activities:create_activity_type'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ActivityType.objects.filter(name='Nouveau type AJAX').exists())

    def test_create_activity_location_ajax(self):
        """Test de la création AJAX d'une salle"""
        data = {
            'name': 'Nouvelle salle AJAX',
            'address': 'Adresse AJAX',
            'capacity': 15,
            'is_active': True
        }
        response = self.client.post(reverse('therapeutic_activities:create_activity_location'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ActivityLocation.objects.filter(name='Nouvelle salle AJAX').exists())


if __name__ == '__main__':
    import django
    django.setup()
    
    # Exécuter les tests
    import unittest
    loader = unittest.TestLoader()
    suite = loader.discover('.')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("Tous les tests ont réussi !")
    else:
        print("Certains tests ont échoué.") 