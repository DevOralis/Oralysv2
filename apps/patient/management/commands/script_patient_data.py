from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import datetime
import json

# Patient models
from apps.patient.models import (
    EmergencyContact,
    Patient,
    Consultation,
    Appointment,
)

# HR (optional – may not be installed in some environments)
try:
    from apps.hr.models import Employee, Speciality
except Exception:  # pragma: no cover
    Employee = None
    Speciality = None

# NOTE:
# 1. You can pass a JSON file exported via `python manage.py dumpdata patient` as an argument:
#    python manage.py script_patient_data <dump.json>
# 2. Otherwise the ``data_json`` variable below will be used.

data = [
    {"model": "patient.emergencycontact", "pk": 20, "fields": {"name": "Ennhili yassine", "phone": "0773694763", "relationship": "Épouse"}}, 
    {"model": "patient.emergencycontact", "pk": 21, "fields": {"name": "ennhili", "phone": "0773694763", "relationship": "Ami(e)"}}, 
    {"model": "patient.emergencycontact", "pk": 24, "fields": {"name": "ali", "phone": "0773694763", "relationship": "Collègue"}}, 
    {"model": "patient.emergencycontact", "pk": 25, "fields": {"name": "ENNHILI", "phone": "0773694763", "relationship": "Ami(e)"}}, 
    {"model": "patient.patient", "pk": 26, "fields": {"patient_identifier": "1234", "cin": "EE000000", "passport_number": "EE000000", "last_name": "ENNHILI", "first_name": "Yassine", "gender": "M", "birth_date": "2025-07-01", "nationality": "MA", "profession": "menuisiser ", "city": "Marrakech", "email": "yassinenhili2002@gmail.com", "phone": "0773694763", "mobile_number": "0773694763", "spouse_name": "halima", "treating_physician": "AYA LAHRAY", "referring_physician": "AYA LAHRAY", "disease_speciality": "", "has_insurance": False, "insurance_number": "123456", "affiliation_number": None, "relationship": "Lui-même", "insured_name": "Yassine", "emergency_contacts": [24]}}, 
    {"model": "patient.patient", "pk": 28, "fields": {"patient_identifier": "1342", "cin": "EE111111", "passport_number": "EE111111", "last_name": "ENNHILI", "first_name": "CHNANEL", "gender": "M", "birth_date": "2025-07-01", "nationality": "AU", "profession": "ingenieur", "city": "Marrakech", "email": "yassinenhili2002@gmail.com", "phone": "0773694763", "mobile_number": "0773694763", "spouse_name": "latifa", "treating_physician": "AYA LAHRAY", "referring_physician": "AYA LAHRAY", "disease_speciality": "", "has_insurance": False, "insurance_number": "090807", "affiliation_number": None, "relationship": "Lui-même", "insured_name": "Yassine", "emergency_contacts": [25]}}, 
    {"model": "patient.consultation", "pk": 18, "fields": {"patient": 28, "medecin": 13, "speciality": 8, "date": "2025-07-29T09:00:00Z", "commentaires": "consultation 1", "traitement": "traitement 1", "temperature": "36.00", "pression": "12/8", "rythme_cardiaque": 80, "hospitalisation": False}}, 
    {"model": "patient.appointment", "pk": 8, "fields": {"patient": 26, "nom": "ENNHILI", "prenom": "Yassine", "telephone": "0773694763", "email": "yassinenhili2002@gmail.com", "medecin": 13, "date_heure": "2025-07-29T09:00:00Z", "motif": "consultation", "statut": "Confirmé", "mode": "Présentiel"}}
]


def parse_date(date_str: str):
    """Return a ``datetime.date`` or ``None`` from an ISO string (YYYY-MM-DD)."""
    if date_str:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    return None


def parse_datetime(date_str: str):
    """Return a ``datetime`` from an ISO string possibly ending with ``Z``."""
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    return None


class Command(BaseCommand):
    """Import fixture-like data for the *patient* app (patients, consultations …)."""

    help = "Insère les données dumpdata pour l'app patient (patients, consultations, etc.)"

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            nargs="?",
            help="Chemin optionnel vers un fichier JSON exporté via `python manage.py dumpdata patient`",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        json_file = options.get("json_file")

        # ---------------------------------------------------------------------
        # 1. Chargement des données
        # ---------------------------------------------------------------------
        if json_file:
            with open(json_file, "r", encoding="utf-8") as jf:
                loaded_data = json.load(jf)
        else:
            loaded_data = data

        if not loaded_data:
            self.stdout.write(self.style.ERROR("Aucune donnée fournie."))
            return

        # ------------------------------------------------------------------
        # 2. Caches pour résolution des clés étrangères / M2M
        # ------------------------------------------------------------------
        objects = {
            "patient.emergencycontact": {},
            "patient.patient": {},
            "patient.consultation": {},
            "patient.appointment": {},
            "hr.employee": {},
            "hr.speciality": {},
        }

        # ------------------------------------------------------------------
        # 3. Parcours et création
        # ------------------------------------------------------------------
        # Petit tri pour importer les dépendances d'abord
        priority = {
            "patient.emergencycontact": 10,
            "patient.patient": 20,
            "patient.consultation": 30,
            "patient.appointment": 40,
        }
        loaded_data.sort(key=lambda x: (priority.get(x["model"], 99), x["pk"]))

        for item in loaded_data:
            model_name = item["model"]
            pk = item["pk"]
            fields = item["fields"]

            try:
                # --------------------- EmergencyContact ---------------------
                if model_name == "patient.emergencycontact":
                    obj = EmergencyContact.objects.create(
                        id=pk,
                        name=fields["name"],
                        phone=fields.get("phone"),
                        relationship=fields.get("relationship", ""),
                    )
                    objects[model_name][pk] = obj

                # --------------------------- Patient -----------------------
                elif model_name == "patient.patient":
                    obj = Patient.objects.create(
                        id=pk,
                        patient_identifier=fields.get("patient_identifier"),
                        cin=fields.get("cin"),
                        passport_number=fields.get("passport_number"),
                        last_name=fields.get("last_name"),
                        first_name=fields.get("first_name"),
                        gender=fields.get("gender"),
                        birth_date=parse_date(fields.get("birth_date")),
                        nationality=fields.get("nationality"),
                        profession=fields.get("profession"),
                        city=fields.get("city"),
                        email=fields.get("email"),
                        phone=fields.get("phone"),
                        mobile_number=fields.get("mobile_number"),
                        spouse_name=fields.get("spouse_name"),
                        treating_physician=fields.get("treating_physician"),
                        referring_physician=fields.get("referring_physician"),
                        disease_speciality=fields.get("disease_speciality"),
                        has_insurance=fields.get("has_insurance", False),
                        insurance_number=fields.get("insurance_number"),
                        affiliation_number=fields.get("affiliation_number"),
                        relationship=fields.get("relationship"),
                        insured_name=fields.get("insured_name"),
                    )
                    # Many-to-many emergency contacts
                    for contact_id in fields.get("emergency_contacts", []):
                        contact = objects["patient.emergencycontact"].get(contact_id)
                        if contact:
                            obj.emergency_contacts.add(contact)
                    objects[model_name][pk] = obj

                # ------------------------- Consultation --------------------
                elif model_name == "patient.consultation":
                    medecin = None
                    speciality = None
                    if Employee:
                        medecin = Employee.objects.filter(pk=fields.get("medecin")).first()
                        if medecin:
                            objects["hr.employee"][medecin.pk] = medecin
                    if Speciality:
                        speciality = Speciality.objects.filter(pk=fields.get("speciality")).first()
                        if speciality:
                            objects["hr.speciality"][speciality.pk] = speciality

                    obj = Consultation.objects.create(
                        id=pk,
                        patient=objects["patient.patient"][fields["patient"]],
                        medecin=medecin,
                        speciality=speciality,
                        date=parse_datetime(fields.get("date")),
                        commentaires=fields.get("commentaires", ""),
                        traitement=fields.get("traitement", ""),
                        temperature=fields.get("temperature"),
                        pression=fields.get("pression"),
                        rythme_cardiaque=fields.get("rythme_cardiaque"),
                        hospitalisation=fields.get("hospitalisation", False),
                    )
                    objects[model_name][pk] = obj

                # ------------------------- Appointment ---------------------
                elif model_name == "patient.appointment":
                    medecin = None
                    if Employee:
                        medecin = Employee.objects.filter(pk=fields.get("medecin")).first()
                        if medecin:
                            objects["hr.employee"][medecin.pk] = medecin

                    obj = Appointment.objects.create(
                        id=pk,
                        patient=objects["patient.patient"].get(fields.get("patient")),
                        nom=fields.get("nom"),
                        prenom=fields.get("prenom"),
                        telephone=fields.get("telephone"),
                        email=fields.get("email"),
                        medecin=medecin,
                        date_heure=parse_datetime(fields.get("date_heure")),
                        motif=fields.get("motif"),
                        statut=fields.get("statut"),
                        mode=fields.get("mode"),
                    )
                    objects[model_name][pk] = obj

                else:
                    # Modèle non géré pour l'instant
                    continue

                self.stdout.write(self.style.SUCCESS(f"Créé {model_name} pk={pk}"))

            except Exception as exc:  # pylint: disable=broad-except
                self.stdout.write(
                    self.style.ERROR(f"Erreur pour {model_name} pk={pk}: {exc}")
                )
                raise

        self.stdout.write(self.style.SUCCESS("Données patient insérées avec succès."))
