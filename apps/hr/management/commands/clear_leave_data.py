from django.core.management.base import BaseCommand
from apps.hr.models import LeaveType, LeaveRequest, LeaveApproval, LeaveBalance
from django.db import transaction

class Command(BaseCommand):
    help = 'Supprime toutes les données liées aux congés'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Supprimer les approbations de congés
                leave_approvals_count = LeaveApproval.objects.all().count()
                LeaveApproval.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f'✓ {leave_approvals_count} approbations de congés supprimées'))

                # Supprimer les demandes de congés
                leave_requests_count = LeaveRequest.objects.all().count()
                LeaveRequest.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f'✓ {leave_requests_count} demandes de congés supprimées'))

                # Supprimer les soldes de congés
                leave_balances_count = LeaveBalance.objects.all().count()
                LeaveBalance.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f'✓ {leave_balances_count} soldes de congés supprimés'))

                # Supprimer les types de congés
                leave_types_count = LeaveType.objects.all().count()
                LeaveType.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f'✓ {leave_types_count} types de congés supprimés'))

                self.stdout.write(self.style.SUCCESS('Toutes les données de congés ont été supprimées avec succès'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Une erreur est survenue: {str(e)}'))
            raise 