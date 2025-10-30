import os
import django
from django.db import transaction
from datetime import datetime
from apps.patient.models import EmergencyContact, Patient, Consultation, Appointment

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oralys.settings')
django.setup()

try:
    from apps.hr.models import Employee, Speciality
except ImportError:
    # Si l'application hr n'existe pas ou n'est pas configurée
    Employee = None
    Speciality = None

# Données JSON
data = [
    {"model": "patient.emergencycontact", "pk": 20, "fields": {"name": "Ennhili yassine", "phone": "0773694763", "relationship": "Épouse"}},
    {"model": "patient.emergencycontact", "pk": 21, "fields": {"name": "ennhili", "phone": "0773694763", "relationship": "Ami(e)"}},
    {"model": "patient.emergencycontact", "pk": 24, "fields": {"name": "ali", "phone": "0773694763", "relationship": "Collègue"}},
    {"model": "patient.emergencycontact", "pk": 25, "fields": {"name": "ENNHILI", "phone": "0773694763", "relationship": "Ami(e)"}},
    {"model": "patient.patient", "pk": 26, "fields": {"patient_identifier": "1234", "cin": "EE000000", "passport_number": "EE000000", "last_name": "ENNHILI", "first_name": "Yassine", "gender": "M", "birth_date": "2025-07-01", "nationality": "MA", "profession": "menuisiser ", "city": "Marrakech", "email": "yassinenhili2002@gmail.com", "phone": "0773694763", "mobile_number": "0773694763", "spouse_name": "halima", "treating_physician": "AYA LAHRAY", "referring_physician": "AYA LAHRAY", "disease_speciality": "", "has_insurance": False, "insurance_number": "123456", "affiliation_number": None, "relationship": "Lui-même", "insured_name": "Yassine", "emergency_contacts": [24]}},
    {"model": "patient.patient", "pk": 28, "fields": {"patient_identifier": "1342", "cin": "EE111111", "passport_number": "EE111111", "last_name": "ENNHILI", "first_name": "CHNANEL", "gender": "M", "birth_date": "2025-07-01", "nationality": "AU", "profession": "ingenieur", "city": "Marrakech", "email": "yassinenhili2002@gmail.com", "phone": "0773694763", "mobile_number": "0773694763", "spouse_name": "latifa", "treating_physician": "AYA LAHRAY", "referring_physician": "AYA LAHRAY", "disease_speciality": "", "has_insurance": False, "insurance_number": "090807", "affiliation_number": None, "relationship": "Lui-même", "insured_name": "Yassine", "emergency_contacts": [25]}},
    {"model": "patient.consultation", "pk": 18, "fields": {"patient": 28, "medecin": 13, "speciality": 8, "date": "2025-07-29T02:40:29.853Z", "commentaires": "walo ", "traitement": "doliprane - vitamine c ", "temperature": "37.0", "pression": "120", "rythme_cardiaque": 98, "hospitalisation": True}},
    {"model": "patient.appointment", "pk": 14, "fields": {"patient": 28, "nom": "ENNHILI", "prenom": "CHNANEL", "telephone": "0773694763", "email": "yassinenhili2002@gmail.com", "medecin": 13, "date_heure": "2025-07-01T01:41:00Z", "motif": "MALDIE", "statut": "effectué", "mode": "mail"}},
    {"model": "patient.appointment", "pk": 15, "fields": {"patient": 26, "nom": "ENNHILI", "prenom": "Yassine", "telephone": "0773694763", "email": "yassinenhili2002@gmail.com", "medecin": 13, "date_heure": "2025-07-29T07:52:00Z", "motif": "MALDIE", "statut": "à venir", "mode": "telephone"}}
]

def parse_datetime(date_str):
    if date_str:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    return None

def parse_date(date_str):
    if date_str:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    return None

objects = {
    'patient.emergencycontact': {},
    'patient.patient': {},
    'patient.consultation': {},
    'patient.appointment': {},
    'hr.employee': {},
    'hr.speciality': {}
}

def main():
    with transaction.atomic():
        for item in data:
            model_name = item['model']
            pk = item['pk']
            fields = item['fields']

            try:
                if model_name == 'patient.emergencycontact':
                    obj = EmergencyContact.objects.create(
                        id=pk,
                        name=fields['name'],
                        phone=fields['phone'],
                        relationship=fields['relationship']
                    )
                    objects[model_name][pk] = obj

                elif model_name == 'patient.patient':
                    obj = Patient(
                        id=pk,
                        patient_identifier=fields['patient_identifier'],
                        cin=fields['cin'],
                        passport_number=fields['passport_number'],
                        last_name=fields['last_name'],
                        first_name=fields['first_name'],
                        gender=fields['gender'],
                        birth_date=parse_date(fields['birth_date']),
                        nationality=fields['nationality'],
                        profession=fields['profession'],
                        city=fields['city'],
                        email=fields['email'],
                        phone=fields['phone'],
                        mobile_number=fields['mobile_number'],
                        spouse_name=fields['spouse_name'],
                        treating_physician=fields['treating_physician'],
                        referring_physician=fields['referring_physician'],
                        disease_speciality=fields['disease_speciality'],
                        has_insurance=fields['has_insurance'],
                        insurance_number=fields['insurance_number'],
                        affiliation_number=fields['affiliation_number'],
                        relationship=fields['relationship'],
                        insured_name=fields['insured_name']
                    )
                    obj.save()
                    for contact_id in fields['emergency_contacts']:
                        obj.emergency_contacts.add(objects['patient.emergencycontact'][contact_id])
                    objects[model_name][pk] = obj

                elif model_name == 'patient.consultation':
                    medecin = None
                    speciality = None
                    if Employee is not None:
                        try:
                            medecin = Employee.objects.get(pk=fields['medecin'])
                            objects['hr.employee'][fields['medecin']] = medecin
                        except Employee.DoesNotExist:
                            print(f"Avertissement : Employé avec pk={fields['medecin']} n'existe pas. Définir medecin à None.")
                    if Speciality is not None:
                        try:
                            speciality = Speciality.objects.get(pk=fields['speciality'])
                            objects['hr.speciality'][fields['speciality']] = speciality
                        except Speciality.DoesNotExist:
                            print(f"Avertissement : Spécialité avec pk={fields['speciality']} n'existe pas. Définir speciality à None.")
                    
                    obj = Consultation(
                        id=pk,
                        patient=objects['patient.patient'][fields['patient']],
                        medecin=medecin,
                        speciality=speciality,
                        date=parse_datetime(fields['date']),
                        commentaires=fields['commentaires'],
                        traitement=fields['traitement'],
                        temperature=fields['temperature'],
                        pression=fields['pression'],
                        rythme_cardiaque=fields['rythme_cardiaque'],
                        hospitalisation=fields['hospitalisation']
                    )
                    obj.save()
                    objects[model_name][pk] = obj

                elif model_name == 'patient.appointment':
                    medecin = None
                    if Employee is not None:
                        try:
                            medecin = Employee.objects.get(pk=fields['medecin'])
                            objects['hr.employee'][fields['medecin']] = medecin
                        except Employee.DoesNotExist:
                            print(f"Avertissement : Employé avec pk={fields['medecin']} n'existe pas. Définir medecin à None.")
                    
                    obj = Appointment(
                        id=pk,
                        patient=objects['patient.patient'][fields['patient']],
                        nom=fields['nom'],
                        prenom=fields['prenom'],
                        telephone=fields['telephone'],
                        email=fields['email'],
                        medecin=medecin,
                        date_heure=parse_datetime(fields['date_heure']),
                        motif=fields['motif'],
                        statut=fields['statut'],
                        mode=fields['mode']
                    )
                    obj.save()
                    objects[model_name][pk] = obj

                print(f"Créé {model_name} avec pk={pk}")

            except Exception as e:
                print(f"Erreur lors de la création de {model_name} avec pk={pk}: {str(e)}")
                raise

        print("Données insérées avec succès.")

if __name__ == '__main__':
    main()