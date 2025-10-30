from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps


class Command(BaseCommand):
    help = 'Réinitialise les séquences des tables pour éviter les conflits de clés primaires'

    def add_arguments(self, parser):
        parser.add_argument(
            '--app',
            type=str,
            default='hr',
            help='Application à traiter (par défaut: hr)'
        )

    def handle(self, *args, **options):
        app_label = options['app']
        
        try:
            # Obtenir tous les modèles de l'app HR
            app_config = apps.get_app_config(app_label)
            models = app_config.get_models()
            
            with connection.cursor() as cursor:
                for model in models:
                    table_name = model._meta.db_table
                    
                    # Vérifier si la table a une séquence (clé primaire auto-incrémentée)
                    pk_field = model._meta.pk
                    if hasattr(pk_field, 'get_internal_type') and pk_field.get_internal_type() in ['AutoField', 'BigAutoField']:
                        
                        # Obtenir le nom de la séquence
                        sequence_name = f"{table_name}_id_seq"
                        
                        # Obtenir la valeur maximale actuelle dans la table
                        cursor.execute(f"SELECT COALESCE(MAX(id), 0) FROM {table_name}")
                        max_id = cursor.fetchone()[0]
                        
                        # Réinitialiser la séquence à max_id + 1
                        new_sequence_value = max_id + 1
                        cursor.execute(f"SELECT setval('{sequence_name}', {new_sequence_value})")
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f' Séquence {sequence_name} réinitialisée à {new_sequence_value}'
                            )
                        )
                        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur lors de la réinitialisation des séquences: {str(e)}')
            )
            return
            
        self.stdout.write(
            self.style.SUCCESS(f'Toutes les séquences de l\'app {app_label} ont été réinitialisées avec succès!')
        )
