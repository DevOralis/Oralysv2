
from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps


class Command(BaseCommand):
    help = 'Réinitialise les séquences des tables pour éviter les conflits de clés primaires'

    def add_arguments(self, parser):
        parser.add_argument(
            '--app',
            type=str,
            default='all',
            help='Nom de l\'application à traiter. Utilisez "all" (ou omettez l\'option) pour traiter toutes les applications.'
        )

    def handle(self, *args, **options):
        app_label = options['app']

        if app_label in (None, '', 'all'):
            app_labels = [cfg.label for cfg in apps.get_app_configs()]
        else:
            app_labels = [app_label]

        try:
            with connection.cursor() as cursor:
                for label in app_labels:
                    app_config = apps.get_app_config(label)
                    models = app_config.get_models()

                    for model in models:
                        table_name = model._meta.db_table
                        pk_field = model._meta.pk

                        if hasattr(pk_field, 'get_internal_type') and pk_field.get_internal_type() in ['AutoField', 'BigAutoField']:
                            pk_column = pk_field.column
                            # PostgreSQL sequences are always lowercase
                            sequence_name = f"{table_name.lower()}_{pk_column}_seq"

                            cursor.execute(f'SELECT COALESCE(MAX("{pk_column}"), 0) FROM "{table_name}"')
                            max_id = cursor.fetchone()[0]

                            new_sequence_value = max_id + 1
                            
                            # Vérifier si la séquence existe avant de la réinitialiser
                            cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_sequences WHERE sequencename = %s)", [sequence_name])
                            sequence_exists = cursor.fetchone()[0]
                            
                            if sequence_exists:
                                cursor.execute("SELECT setval(%s, %s)", [sequence_name, new_sequence_value])
                                self.stdout.write(self.style.SUCCESS(
                                    f"Séquence {sequence_name} réinitialisée à {new_sequence_value} (app: {label})"))
                            else:
                                self.stdout.write(self.style.WARNING(
                                    f"Séquence {sequence_name} introuvable, ignorée (app: {label})"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Erreur lors de la réinitialisation des séquences: {str(e)}"))
            return

        self.stdout.write(self.style.SUCCESS("Toutes les séquences ont été réinitialisées avec succès!"))
