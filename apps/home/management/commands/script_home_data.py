from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import datetime
import json

from apps.home.models import User, UserPermission
from apps.hr.models import Employee




data = [
    {"model": "home.user", "pk": 6, "fields": {"last_login": "2025-08-16T16:00:27.970Z", "nom": "YASSINE", "prenom": "ENNHILI", "username": "CLV01", "password": "pbkdf2_sha256$1000000$dUYE7Pojz9ZYt3ApDXhvEb$QTqnYv9Nov6JSJ3+NAO74LsyOILi6JWpUPwpr1G2Y14=", "is_activated": True, "employee": 14, "is_staff": False, "is_superuser": False, "date_joined": "2025-08-14T04:48:53.179Z", "groups": [], "user_permissions": []}}, 
    {"model": "home.user", "pk": 8, "fields": {"last_login": "2025-08-15T16:26:27.996Z", "nom": "Berrouch", "prenom": "Kawtar", "username": "CLV02", "password": "pbkdf2_sha256$1000000$sKcJ7IE7fI2jne2Ytj1mKd$GCPt3yxQNQRNiMapdbDID4lkxhGDGMS2iBx2/qu3owI=", "is_activated": True, "employee": 15, "is_staff": False, "is_superuser": False, "date_joined": "2025-08-14T09:24:35.713Z", "groups": [], "user_permissions": []}}, 
    {"model": "home.user", "pk": 22, "fields": {"last_login": "2025-08-16T16:01:00.449Z", "nom": "YASSINE", "prenom": "YASSINE", "username": "YASSINE", "password": "pbkdf2_sha256$1000000$P4T6KlW9Tcyzi6iMmRVL4Y$CHg/sGVTu/S6m1UlXkp9FR+Q+R/apV6x/tJPCP3qZuc=", "is_activated": True, "employee": None, "is_staff": True, "is_superuser": True, "date_joined": "2025-08-16T14:38:03.878Z", "groups": [], "user_permissions": []}}, 
    {"model": "home.user", "pk": 31, "fields": {"last_login": None, "nom": "ENNHILI", "prenom": "OMAR", "username": "CLV03", "password": "pbkdf2_sha256$1000000$iKFfiEdZb03Dt4iMizhVZt$NJ6s3drjbno/YK6mv4nIpTI+QNfOhm3vU7YNr50qFLE=", "is_activated": True, "employee": 16, "is_staff": False, "is_superuser": False, "date_joined": "2025-08-16T16:01:47.615Z", "groups": [], "user_permissions": []}}, 
    {"model": "home.user", "pk": 32, "fields": {"last_login": None, "nom": "erramach", "prenom": "HASSNAe", "username": "CLV04", "password": "pbkdf2_sha256$1000000$8V145LmWiTRu2TvaJcTb7p$cZksn5HsQArJ+QGBdf1b+8sSJ9iFis062gYG/qyu6EA=", "is_activated": True, "employee": 4, "is_staff": False, "is_superuser": False, "date_joined": "2025-08-16T16:02:46.632Z", "groups": [], "user_permissions": []}}, 
    {"model": "home.user", "pk": 33, "fields": {"last_login": "2025-08-16T16:05:34.341Z", "nom": "ABDELMOUGHITH", "prenom": "ABDELMOUGHITH", "username": "ABDELMOUGHITH", "password": "pbkdf2_sha256$1000000$L58w5kLeAPggs7w674LMH9$FgrXnssxw1HVCF0mbzHAGe0TYpw3YZz6ghmiTWy8/EI=", "is_activated": True, "employee": None, "is_staff": True, "is_superuser": True, "date_joined": "2025-08-16T16:04:01.618Z", "groups": [], "user_permissions": []}}, 
    {"model": "home.user", "pk": 34, "fields": {"last_login": None, "nom": "KAWTAR", "prenom": "KAWTAR", "username": "KAWTAR", "password": "pbkdf2_sha256$1000000$5JOJqTsEIsRvZscDjPo81Z$3KGZe7ItvBLS+N4irjtCd+zKcR8WexVfRUi5yMT+/2M=", "is_activated": True, "employee": None, "is_staff": True, "is_superuser": True, "date_joined": "2025-08-16T16:04:52.539Z", "groups": [], "user_permissions": []}}, 
    {"model": "home.userpermission", "pk": 1, "fields": {"user": 6, "app_name": "apps.home", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 2, "fields": {"user": 6, "app_name": "apps.hr", "can_read": True, "can_write": True, "can_update": True, "can_delete": True}}, 
    {"model": "home.userpermission", "pk": 3, "fields": {"user": 6, "app_name": "apps.formation", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 4, "fields": {"user": 6, "app_name": "apps.purchases", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 5, "fields": {"user": 6, "app_name": "apps.inventory", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 6, "fields": {"user": 6, "app_name": "apps.pharmacy", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 7, "fields": {"user": 6, "app_name": "apps.patient", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 8, "fields": {"user": 6, "app_name": "apps.therapeutic_activities", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 9, "fields": {"user": 6, "app_name": "apps.recruitment", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 19, "fields": {"user": 8, "app_name": "apps.home", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 20, "fields": {"user": 8, "app_name": "apps.hr", "can_read": True, "can_write": True, "can_update": True, "can_delete": True}}, 
    {"model": "home.userpermission", "pk": 21, "fields": {"user": 8, "app_name": "apps.formation", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 22, "fields": {"user": 8, "app_name": "apps.purchases", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 23, "fields": {"user": 8, "app_name": "apps.inventory", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 24, "fields": {"user": 8, "app_name": "apps.pharmacy", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 25, "fields": {"user": 8, "app_name": "apps.patient", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 26, "fields": {"user": 8, "app_name": "apps.therapeutic_activities", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 27, "fields": {"user": 8, "app_name": "apps.recruitment", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 236, "fields": {"user": 31, "app_name": "apps.home", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 237, "fields": {"user": 31, "app_name": "apps.hr", "can_read": True, "can_write": True, "can_update": True, "can_delete": True}}, 
    {"model": "home.userpermission", "pk": 238, "fields": {"user": 31, "app_name": "apps.formation", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 239, "fields": {"user": 31, "app_name": "apps.purchases", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 240, "fields": {"user": 31, "app_name": "apps.inventory", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 241, "fields": {"user": 31, "app_name": "apps.pharmacy", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 242, "fields": {"user": 31, "app_name": "apps.patient", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 243, "fields": {"user": 31, "app_name": "apps.therapeutic_activities", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 244, "fields": {"user": 31, "app_name": "apps.recruitment", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 245, "fields": {"user": 32, "app_name": "apps.home", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 246, "fields": {"user": 32, "app_name": "apps.hr", "can_read": True, "can_write": True, "can_update": True, "can_delete": True}}, 
    {"model": "home.userpermission", "pk": 247, "fields": {"user": 32, "app_name": "apps.formation", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 248, "fields": {"user": 32, "app_name": "apps.purchases", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 249, "fields": {"user": 32, "app_name": "apps.inventory", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 250, "fields": {"user": 32, "app_name": "apps.pharmacy", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 251, "fields": {"user": 32, "app_name": "apps.patient", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 252, "fields": {"user": 32, "app_name": "apps.therapeutic_activities", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}, 
    {"model": "home.userpermission", "pk": 253, "fields": {"user": 32, "app_name": "apps.recruitment", "can_read": False, "can_write": False, "can_update": False, "can_delete": False}}
]

def parse_datetime(date_str: str):
    """Convertit une chaîne ISO 8601 (terminant par 'Z') en objet datetime."""
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    return None


class Command(BaseCommand):
    help = "Insère les données dumpdata pour l'app home (User & UserPermission)"

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            nargs="?",
            help="Chemin optionnel vers le fichier JSON exporté via `python manage.py dumpdata home`",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        json_file = options.get("json_file")

        # 1. Chargement des données ------------------------------------------------
        if json_file:
            with open(json_file, "r", encoding="utf-8") as jf:
                loaded_data = json.load(jf)
        else:
            loaded_data = data

        if not loaded_data:
            self.stdout.write(self.style.ERROR("Aucune donnée fournie."))
            return

        # 2. Caches d'objets déjà créés -------------------------------------------
        objects = {
            "home.user": {},
            "home.userpermission": {},
        }

        # 3. Parcours et création --------------------------------------------------
        for item in loaded_data:
            model_name = item["model"]
            pk = item["pk"]
            fields = item["fields"]

            try:
                if model_name == "home.user":
                    # Création de l'utilisateur (mot de passe déjà chiffré)
                    obj = User.objects.create(
                        id=pk,
                        last_login=parse_datetime(fields["last_login"]) if fields["last_login"] else None,
                        nom=fields["nom"],
                        prenom=fields["prenom"],
                        username=fields["username"],
                        password=fields["password"],
                        is_activated=fields["is_activated"],
                        employee=Employee.objects.get(pk=fields["employee"]) if fields["employee"] else None,
                        is_staff=fields["is_staff"],
                        is_superuser=fields["is_superuser"],
                        date_joined=parse_datetime(fields["date_joined"]),
                    )
                    objects[model_name][pk] = obj

                    # TODO: gérer groups et user_permissions M2M si nécessaire

                elif model_name == "home.userpermission":
                    obj = UserPermission.objects.create(
                        id=pk,
                        user=objects["home.user"][fields["user"]],
                        app_name=fields["app_name"],
                        can_read=fields["can_read"],
                        can_write=fields["can_write"],
                        can_update=fields["can_update"],
                        can_delete=fields["can_delete"],
                    )
                    objects[model_name][pk] = obj

                else:
                    # Modèle non géré
                    continue

                self.stdout.write(self.style.SUCCESS(f"Créé {model_name} pk={pk}"))

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Erreur lors de la création de {model_name} pk={pk}: {e}")
                )
                raise

        self.stdout.write(self.style.SUCCESS("Données home insérées avec succès."))
