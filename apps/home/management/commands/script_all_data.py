from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    
    help = "Exécute tous les scripts d'import de données (hr -> patient) dans le bon ordre."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip",
            nargs="*",
            default=[],
            help="Liste d'apps à ignorer (ex: --skip patient purchases)",
            choices=[
                "hr",
                "home",
                "inventory",
                "purchases",
                "pharmacy",
                "patient",
                "hosting",
                "therapeutic_activities",
            ],
        )

    def handle(self, *args, **options):
        skip = set(options.get("skip", []))

        sequence = [
            ("hr", "script_hr_data"),
            ("home", "script_home_data"),
            ("inventory", "script_inventory_data"),
            ("purchases", "script_purchases_data"),
            ("pharmacy", "script_pharmacy_data"),
            ("patient", "script_patient_data"),
            ("hosting", "script_hosting_data"),
            ("therapeutic_activities", "script_therapeutic_data"),
        ]

        for app_label, command_name in sequence:
            if app_label in skip:
                self.stdout.write(self.style.WARNING(f"— {app_label} ignoré"))
                continue

            self.stdout.write(self.style.MIGRATE_HEADING(f"==> Import {app_label}…"))
            try:
                call_command(command_name)
                self.stdout.write(self.style.SUCCESS(f"✓  Import {app_label} terminé"))
            except Exception as exc:  # pylint: disable=broad-except
                self.stdout.write(self.style.ERROR(f"✗  Échec import {app_label}: {exc}"))
                raise  # stop le processus sur erreur

        self.stdout.write(self.style.SUCCESS("Import complet terminé."))
