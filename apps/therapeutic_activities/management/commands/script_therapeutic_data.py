from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from datetime import datetime, date, time

from apps.therapeutic_activities.models import (
    ActivityType, ActivityLocation, Activity, Session, Participation,
    ErgotherapyEvaluation, CoachingSession, SocialReport
)
from apps.hr.models import Employee
from apps.patient.models import Patient


class Command(BaseCommand):
    help = 'Populates the therapeutic activities database with initial data'

    @transaction.atomic
    def handle(self, *args, **options):
        
        # Créer ActivityType
        try:
            activity_type1 = ActivityType.objects.create(
                id=5,
                name="Ergothérapie",
                description="Description pour Ergothérapie",
                is_active=True,
                created_at=datetime(2025, 8, 23, 8, 19, 44, 730000),
                updated_at=datetime(2025, 8, 23, 8, 19, 44, 730000)
            )
            self.stdout.write(self.style.SUCCESS(f"Créé ActivityType: {activity_type1.name}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"ActivityType Ergothérapie existe déjà ou erreur: {e}"))

        try:
            activity_type2 = ActivityType.objects.create(
                id=6,
                name="Art-thérapie",
                description="Description pour Art-thérapie",
                is_active=True,
                created_at=datetime(2025, 8, 23, 8, 19, 44, 742000),
                updated_at=datetime(2025, 8, 23, 8, 19, 44, 742000)
            )
            self.stdout.write(self.style.SUCCESS(f"Créé ActivityType: {activity_type2.name}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"ActivityType Art-thérapie existe déjà ou erreur: {e}"))

        try:
            activity_type_group = ActivityType.objects.create(
                id=9,
                name="Groupe de parole",
                description="Description pour Groupe de parole",
                is_active=True,
                created_at=datetime(2025, 8, 23, 8, 19, 44, 751000),
                updated_at=datetime(2025, 8, 23, 8, 19, 44, 751000)
            )
            self.stdout.write(self.style.SUCCESS(f"Créé ActivityType: {activity_type_group.name}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"ActivityType Groupe de parole existe déjà ou erreur: {e}"))

        # Créer ActivityLocation
        try:
            location1 = ActivityLocation.objects.create(
                id=3,
                name="Salle de thérapie 1",
                address="Bâtiment A, RDC",
                capacity=10,
                is_active=True,
                created_at=datetime(2025, 8, 23, 8, 19, 44, 757000),
                updated_at=datetime(2025, 8, 23, 8, 19, 44, 757000)
            )
            self.stdout.write(self.style.SUCCESS(f"Créé ActivityLocation: {location1.name}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"ActivityLocation Salle de thérapie 1 existe déjà ou erreur: {e}"))

        try:
            location2 = ActivityLocation.objects.create(
                id=4,
                name="Salle de thérapie 2",
                address="Bâtiment A, 1er étage",
                capacity=15,
                is_active=True,
                created_at=datetime(2025, 8, 23, 8, 19, 44, 763000),
                updated_at=datetime(2025, 8, 23, 8, 19, 44, 763000)
            )
            self.stdout.write(self.style.SUCCESS(f"Créé ActivityLocation: {location2.name}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"ActivityLocation Salle de thérapie 2 existe déjà ou erreur: {e}"))

        # Récupérer les objets créés ou existants
        activity_type_group = ActivityType.objects.get(id=9)  # Groupe de parole doit exister
        activity_type_art = ActivityType.objects.get(id=6)
        coach1 = Employee.objects.get(pk=20)
        coach2 = Employee.objects.get(pk=4)
        location1 = ActivityLocation.objects.get(id=3)
        location2 = ActivityLocation.objects.get(id=4)

        # Créer Activity
        try:
            activity1 = Activity.objects.create(
                id=10,
                title="Groupe de parole 1",
                description="Description détaillée pour l'activité Groupe de parole 1",
                type=activity_type_group,
                coach=coach1,
                is_active=True,
                created_at=datetime(2025, 8, 23, 8, 19, 44, 784000),
                updated_at=datetime(2025, 8, 23, 8, 19, 44, 784000)
            )
            self.stdout.write(self.style.SUCCESS(f"Créé Activity: {activity1.title}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Activity Groupe de parole 1 existe déjà ou erreur: {e}"))

        try:
            activity2 = Activity.objects.create(
                id=11,
                title="Art-thérapie 2",
                description="Description détaillée pour l'activité Art-thérapie 2",
                type=activity_type_art,
                coach=coach2,
                is_active=True,
                created_at=datetime(2025, 8, 23, 8, 19, 44, 788000),
                updated_at=datetime(2025, 8, 23, 8, 19, 44, 788000)
            )
            self.stdout.write(self.style.SUCCESS(f"Créé Activity: {activity2.title}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Activity Art-thérapie 2 existe déjà ou erreur: {e}"))

        # Récupérer les activités
        activity1 = Activity.objects.get(id=10)
        activity2 = Activity.objects.get(id=11)

        # Créer Session
        try:
            session1 = Session.objects.create(
                id=6,
                activity=activity1,
                location=location1,
                date=date(2025, 9, 8),
                start_time=time(13, 0, 0),
                end_time=time(16, 0, 0),
                max_participants=13,
                status="planned",
                notes="",
                created_at=datetime(2025, 8, 23, 8, 19, 44, 819000),
                updated_at=datetime(2025, 8, 23, 8, 19, 44, 819000)
            )
            self.stdout.write(self.style.SUCCESS(f"Créé Session: {session1.id} pour {session1.activity.title}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Session 6 existe déjà ou erreur: {e}"))

        try:
            session2 = Session.objects.create(
                id=7,
                activity=activity2,
                location=location2,
                date=date(2025, 9, 3),
                start_time=time(9, 0, 0),
                end_time=time(12, 0, 0),
                max_participants=10,
                status="planned",
                notes="",
                created_at=datetime(2025, 8, 23, 8, 19, 44, 822000),
                updated_at=datetime(2025, 8, 23, 8, 19, 44, 822000)
            )
            self.stdout.write(self.style.SUCCESS(f"Créé Session: {session2.id} pour {session2.activity.title}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Session 7 existe déjà ou erreur: {e}"))

        # Récupérer les sessions
        session1 = Session.objects.get(id=6)
        session2 = Session.objects.get(id=7)

        # Récupérer les patients
        patient1 = Patient.objects.get(pk=28)  # CHNANEL ENNHILI
        patient2 = Patient.objects.get(pk=26)  # Yassine ENNHILI

        # Créer Participation
        try:
            participation1 = Participation.objects.create(
                id=42,
                patient=patient1,
                session=session1,
                status="excused",
                notes="",
                created_at=datetime(2025, 8, 23, 8, 19, 44, 890000),
                updated_at=datetime(2025, 8, 23, 8, 19, 44, 890000)
            )
            self.stdout.write(self.style.SUCCESS(f"Créé Participation: {participation1.id}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Participation 42 existe déjà ou erreur: {e}"))

        try:
            participation2 = Participation.objects.create(
                id=43,
                patient=patient2,
                session=session1,
                status="excused",
                notes="",
                created_at=datetime(2025, 8, 23, 8, 19, 44, 894000),
                updated_at=datetime(2025, 8, 23, 8, 19, 44, 894000)
            )
            self.stdout.write(self.style.SUCCESS(f"Créé Participation: {participation2.id}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Participation 43 existe déjà ou erreur: {e}"))

        # Récupérer les participations
        participation1 = Participation.objects.get(id=42)
        participation2 = Participation.objects.get(id=43)

        # Créer ErgotherapyEvaluation
        try:
            eval1 = ErgotherapyEvaluation.objects.create(
                id=2,
                participation=participation1,
                rosenberg_score=Decimal("29.57118796772267"),
                moca_score=Decimal("24.729767898864953"),
                osa_result="Résultat OSA pour Houda Benomar",
                goals="Objectifs thérapeutiques pour Houda Benomar",
                evaluation_date=date(2025, 8, 23),
                created_at=datetime(2025, 8, 23, 8, 19, 44, 976000),
                updated_at=datetime(2025, 8, 23, 8, 19, 44, 976000)
            )
            self.stdout.write(self.style.SUCCESS(f"Créé ErgotherapyEvaluation: {eval1.id}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"ErgotherapyEvaluation 2 existe déjà ou erreur: {e}"))

        try:
            eval2 = ErgotherapyEvaluation.objects.create(
                id=3,
                participation=participation2,
                rosenberg_score=Decimal("19.131109046434"),
                moca_score=Decimal("24.141824462871714"),
                osa_result="Résultat OSA pour Hassan Sabri",
                goals="Objectifs thérapeutiques pour Hassan Sabri",
                evaluation_date=date(2025, 8, 23),
                created_at=datetime(2025, 8, 23, 8, 19, 44, 980000),
                updated_at=datetime(2025, 8, 23, 8, 19, 44, 980000)
            )
            self.stdout.write(self.style.SUCCESS(f"Créé ErgotherapyEvaluation: {eval2.id}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"ErgotherapyEvaluation 3 existe déjà ou erreur: {e}"))

        # Créer CoachingSession
        try:
            coaching1 = CoachingSession.objects.create(
                id=3,
                participation=participation1,
                plan="Plan de coaching pour Houda Benomar",
                result="Résultats initiaux pour Houda Benomar",
                session_date=date(2025, 8, 23),
                created_at=datetime(2025, 8, 23, 8, 19, 44, 991000),
                updated_at=datetime(2025, 8, 23, 8, 19, 44, 991000)
            )
            self.stdout.write(self.style.SUCCESS(f"Créé CoachingSession: {coaching1.id}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"CoachingSession 3 existe déjà ou erreur: {e}"))

        try:
            coaching2 = CoachingSession.objects.create(
                id=4,
                participation=participation2,
                plan="Plan de coaching pour Hassan Sabri",
                result="Résultats initiaux pour Hassan Sabri",
                session_date=date(2025, 8, 23),
                created_at=datetime(2025, 8, 23, 8, 19, 44, 993000),
                updated_at=datetime(2025, 8, 23, 8, 19, 44, 993000)
            )
            self.stdout.write(self.style.SUCCESS(f"Créé CoachingSession: {coaching2.id}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"CoachingSession 4 existe déjà ou erreur: {e}"))

        # Créer SocialReport
        try:
            report1 = SocialReport.objects.create(
                id=3,
                participation=participation1,
                intervention_plan="Plan d'intervention pour Houda Benomar",
                interview_notes="Notes d'entretien pour Houda Benomar",
                exit_summary="Résumé de sortie pour Houda Benomar",
                meeting_notes="Notes de réunion pour Houda Benomar",
                report_date=date(2025, 8, 23),
                created_at=datetime(2025, 8, 23, 8, 19, 45, 5000),
                updated_at=datetime(2025, 8, 23, 8, 19, 45, 5000)
            )
            self.stdout.write(self.style.SUCCESS(f"Créé SocialReport: {report1.id}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"SocialReport 3 existe déjà ou erreur: {e}"))

        try:
            report2 = SocialReport.objects.create(
                id=4,
                participation=participation2,
                intervention_plan="Plan d'intervention pour Hassan Sabri",
                interview_notes="Notes d'entretien pour Hassan Sabri",
                exit_summary="Résumé de sortie pour Hassan Sabri",
                meeting_notes="Notes de réunion pour Hassan Sabri",
                report_date=date(2025, 8, 23),
                created_at=datetime(2025, 8, 23, 8, 19, 45, 8000),
                updated_at=datetime(2025, 8, 23, 8, 19, 45, 8000)
            )
            self.stdout.write(self.style.SUCCESS(f"Créé SocialReport: {report2.id}"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"SocialReport 4 existe déjà ou erreur: {e}"))

        self.stdout.write(self.style.SUCCESS('✅ Données therapeutic_activities insérées avec succès!'))
