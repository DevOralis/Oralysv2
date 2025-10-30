import os
import django
from django.db import transaction
from decimal import Decimal
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.hr.models import (
    Department, Position, ContractType, Contract, Child, Employee,
    SocialContribution, Prime, ModelCalcul, Speciality, LeaveType,
    LeaveBalance, PayrollGenerationHistory
)

# Données JSON
data = [
    {"model": "hr.department", "pk": 1, "fields": {"name": "Administration", "description": None, "parent": None, "created_at": "2025-07-01T22:56:58.644Z", "updated_at": "2025-07-01T22:56:58.644Z"}},
    {"model": "hr.department", "pk": 2, "fields": {"name": "Urgences", "description": None, "parent": None, "created_at": "2025-07-01T22:57:23.037Z", "updated_at": "2025-07-01T22:57:23.037Z"}},
    {"model": "hr.department", "pk": 3, "fields": {"name": "Pédiatrie", "description": None, "parent": None, "created_at": "2025-07-01T22:57:47.447Z", "updated_at": "2025-07-01T22:57:47.447Z"}},
    {"model": "hr.department", "pk": 4, "fields": {"name": "Pharmacie", "description": None, "parent": None, "created_at": "2025-07-01T22:57:57.466Z", "updated_at": "2025-07-01T22:57:57.466Z"}},
    {"model": "hr.position", "pk": 1, "fields": {"name": "Infirmier", "description": None, "created_at": "2025-07-01T22:28:55.769Z", "updated_at": "2025-07-20T13:50:09.664Z"}},
    {"model": "hr.position", "pk": 2, "fields": {"name": "Ressources Humaines", "description": None, "created_at": "2025-07-01T22:55:01.136Z", "updated_at": "2025-07-01T22:55:01.136Z"}},
    {"model": "hr.position", "pk": 3, "fields": {"name": "Médecin ", "description": None, "created_at": "2025-07-01T22:55:26.804Z", "updated_at": "2025-07-10T11:38:50.814Z"}},
    {"model": "hr.position", "pk": 4, "fields": {"name": "Médecin Vacataire", "description": None, "created_at": "2025-07-01T22:55:42.176Z", "updated_at": "2025-07-01T22:55:42.176Z"}},
    {"model": "hr.position", "pk": 5, "fields": {"name": "Secrétaire", "description": None, "created_at": "2025-07-01T22:56:32.632Z", "updated_at": "2025-07-01T22:56:32.632Z"}},
    {"model": "hr.position", "pk": 6, "fields": {"name": "Technicien", "description": None, "created_at": "2025-07-01T22:56:44.786Z", "updated_at": "2025-07-01T22:56:44.786Z"}},
    {"model": "hr.position", "pk": 18, "fields": {"name": "Coach", "description": None, "created_at": "2025-07-25T13:30:50.141Z", "updated_at": "2025-07-25T13:30:50.143Z"}},
    {"model": "hr.contracttype", "pk": 1, "fields": {"name": "CDD", "description": None, "created_at": "2025-07-01T22:58:15.832Z", "updated_at": "2025-07-01T22:58:15.832Z"}},
    {"model": "hr.contracttype", "pk": 2, "fields": {"name": "CDI", "description": None, "created_at": "2025-07-01T22:58:22.788Z", "updated_at": "2025-07-01T22:58:22.788Z"}},
    {"model": "hr.contracttype", "pk": 3, "fields": {"name": "ANAPEC", "description": None, "created_at": "2025-07-01T22:58:33.795Z", "updated_at": "2025-07-03T06:11:59.910Z"}},
    {"model": "hr.contract", "pk": 21, "fields": {"employee": 4, "start_date": "2025-07-30", "end_date": None, "contract_type": 3, "created_at": "2025-07-22T11:20:50.225Z", "updated_at": "2025-07-22T11:20:50.225Z"}},
    {"model": "hr.contract", "pk": 22, "fields": {"employee": 12, "start_date": "2025-07-01", "end_date": None, "contract_type": 3, "created_at": "2025-07-22T11:27:12.610Z", "updated_at": "2025-07-25T12:31:28.030Z"}},
    {"model": "hr.child", "pk": 54, "fields": {"name": "OUALID", "gender": "M", "birth_date": None, "is_scolarise": False, "created_at": "2025-07-22T11:20:50.209Z", "updated_at": "2025-07-22T11:20:50.209Z"}},
    {"model": "hr.child", "pk": 55, "fields": {"name": "yassi neennhili", "gender": "M", "birth_date": None, "is_scolarise": False, "created_at": "2025-07-22T11:20:50.218Z", "updated_at": "2025-07-22T11:20:50.218Z"}},
    {"model": "hr.child", "pk": 67, "fields": {"name": "omar omar", "gender": "M", "birth_date": None, "is_scolarise": False, "created_at": "2025-07-25T12:31:28.021Z", "updated_at": "2025-07-25T12:31:28.021Z"}},
    {"model": "hr.child", "pk": 68, "fields": {"name": "yassi neennhili", "gender": "M", "birth_date": None, "is_scolarise": False, "created_at": "2025-07-25T12:31:28.021Z", "updated_at": "2025-07-25T12:31:28.021Z"}},
    {"model": "hr.socialcontribution", "pk": 2, "fields": {"label": "CNSS", "rate": "3.96", "ceiling": "6000.00"}},
    {"model": "hr.socialcontribution", "pk": 3, "fields": {"label": "AMO", "rate": "2.26", "ceiling": "0.00"}},
    {"model": "hr.socialcontribution", "pk": 5, "fields": {"label": "frais professionnelles", "rate": "20.00", "ceiling": "500.00"}},
    {"model": "hr.socialcontribution", "pk": 9, "fields": {"label": "CIMR", "rate": "3.00", "ceiling": None}},
    {"model": "hr.prime", "pk": 8, "fields": {"libelle": "Prime D'aciennete ", "rate": "5.00", "amount": None}},
    {"model": "hr.prime", "pk": 13, "fields": {"libelle": "Prime de transport ", "rate": None, "amount": "500.00"}},
    {"model": "hr.prime", "pk": 15, "fields": {"libelle": "Prime de repas", "rate": None, "amount": "300.00"}},
    {"model": "hr.prime", "pk": 18, "fields": {"libelle": "prime de Logement", "rate": None, "amount": "500.00"}},
    {"model": "hr.modelcalcul", "pk": 4, "fields": {"libelle": "model X", "social_contributions": [2, 3, 9], "primes": [8, 18]}},
    {"model": "hr.modelcalcul", "pk": 6, "fields": {"libelle": "model Y", "social_contributions": [2, 3, 5], "primes": [8, 13, 15, 18]}},
    {"model": "hr.modelcalcul", "pk": 7, "fields": {"libelle": "model Z", "social_contributions": [2, 3, 9], "primes": [8, 13, 15, 18]}},
    {"model": "hr.speciality", "pk": 8, "fields": {"name": "Psychiatrie"}},
    {"model": "hr.speciality", "pk": 9, "fields": {"name": "PedoPsychiatrie"}},
    {"model": "hr.speciality", "pk": 10, "fields": {"name": "Sexologie"}},
    {"model": "hr.speciality", "pk": 11, "fields": {"name": "Psychologie clinique"}},
    {"model": "hr.speciality", "pk": 12, "fields": {"name": "Neurologie / Neuropsychologie"}},
    {"model": "hr.speciality", "pk": 13, "fields": {"name": "Addictologie "}},
    {"model": "hr.speciality", "pk": 14, "fields": {"name": "Orthophonie / Logopédie "}},
    {"model": "hr.speciality", "pk": 15, "fields": {"name": "Éducation spécialisée / Psychopédagogie "}},
    {"model": "hr.speciality", "pk": 16, "fields": {"name": "Gérontopsychiatrie"}},
    {"model": "hr.employee", "pk": 4, "fields": {"employee_id": "A3", "national_id": "EE333333", "full_name": "HASSNAe erramach", "birth_date": "2025-06-29", "photo": "hr_media/employees_profile/WhatsApp_Image_2025-06-29_at_12.07.57_d0550036.jpg", "marital_status": "M", "gender": "F", "email": "hassna200@gmail.com", "personal_phone": "0733333333", "work_phone": "0733333333", "personal_address": "mabrouka", "work_address": "EC 12 ", "children_count": 1, "status": "A", "position": 5, "department": 1, "speciality": None, "work_certificate": "", "legalized_contract": "hr_media/legalized_contracts/Forum_International_sur_la_Chasse_Durable_International_For_X9h7Uiz.pdf", "doctor_agreement": "", "temporary_agreement": "", "base_salary": "2300.00", "model_calcul": 4, "career_evolution": "PR HASSNA ERRAMACH", "skills": "CS", "is_supervisor": 1, "supervisor": None, "children": [54, 55]}},
    {"model": "hr.employee", "pk": 12, "fields": {"employee_id": "A0", "national_id": "EE000000", "full_name": "Ennhili yassine", "birth_date": "2025-07-01", "photo": "hr_media/employees_profile/6_GGjcWNN.png", "marital_status": "S", "gender": "M", "email": "yassinenhili2002@gmail.com", "personal_phone": "0773694763", "work_phone": "0773694763", "personal_address": "fkuyf", "work_address": "vhhk", "children_count": 1, "status": "A", "position": 1, "department": 1, "speciality": None, "work_certificate": "", "legalized_contract": "hr_media/legalized_contracts/citeinnovation.pdf", "doctor_agreement": "", "temporary_agreement": "", "base_salary": "5000.00", "model_calcul": 4, "career_evolution": "agiur", "skills": "SR", "is_supervisor": 1, "supervisor": None, "children": [67, 68]}},
    {"model": "hr.leavetype", "pk": 24, "fields": {"name": "conge maladie", "default_days": None, "accrual_method": "annual", "year": 2024, "active": True, "monday": True, "tuesday": True, "wednesday": True, "thursday": True, "friday": True, "saturday": True, "sunday": False, "description": "merci"}},
    {"model": "hr.leavetype", "pk": 25, "fields": {"name": "Conge annuel", "default_days": "24.00", "accrual_method": "annual", "year": 2024, "active": True, "monday": True, "tuesday": True, "wednesday": True, "thursday": True, "friday": True, "saturday": False, "sunday": False, "description": "maladie"}},
    {"model": "hr.leavetype", "pk": 26, "fields": {"name": "conge exceptionnel", "default_days": None, "accrual_method": "annual", "year": 2024, "active": True, "monday": True, "tuesday": True, "wednesday": True, "thursday": True, "friday": True, "saturday": False, "sunday": False, "description": "wqe"}},
    {"model": "hr.leavebalance", "pk": 50, "fields": {"employee": 4, "leave_type": 26, "year": 2025, "entitlement": "0.00", "taken": "0.00", "remaining": "0.00"}},
    {"model": "hr.leavebalance", "pk": 51, "fields": {"employee": 4, "leave_type": 25, "year": 2025, "entitlement": "24.00", "taken": "0.00", "remaining": "24.00"}},
    {"model": "hr.leavebalance", "pk": 53, "fields": {"employee": 4, "leave_type": 24, "year": 2025, "entitlement": "0.00", "taken": "0.00", "remaining": "0.00"}},
    {"model": "hr.payrollgenerationhistory", "pk": 13, "fields": {"employee": 12, "generated_by": None, "generated_at": "2025-07-24T21:47:29.646Z", "start_date": "2025-07-01", "end_date": "2025-07-31"}}
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
    'hr.department': {},
    'hr.position': {},
    'hr.contracttype': {},
    'hr.contract': {},
    'hr.child': {},
    'hr.employee': {},
    'hr.socialcontribution': {},
    'hr.prime': {},
    'hr.modelcalcul': {},
    'hr.speciality': {},
    'hr.leavetype': {},
    'hr.leavebalance': {},
    'hr.payrollgenerationhistory': {}
}

def main():
    with transaction.atomic():
        for item in data:
            model_name = item['model']
            pk = item['pk']
            fields = item['fields']

            try:
                if model_name == 'hr.department':
                    obj = Department.objects.create(
                        id=pk,
                        name=fields['name'],
                        description=fields['description'],
                        parent_id=fields['parent'],
                        created_at=parse_datetime(fields['created_at']),
                        updated_at=parse_datetime(fields['updated_at'])
                    )
                    objects[model_name][pk] = obj

                elif model_name == 'hr.position':
                    obj = Position.objects.create(
                        id=pk,
                        name=fields['name'],
                        description=fields['description'],
                        created_at=parse_datetime(fields['created_at']),
                        updated_at=parse_datetime(fields['updated_at'])
                    )
                    objects[model_name][pk] = obj

                elif model_name == 'hr.contracttype':
                    obj = ContractType.objects.create(
                        id=pk,
                        name=fields['name'],
                        description=fields['description'],
                        created_at=parse_datetime(fields['created_at']),
                        updated_at=parse_datetime(fields['updated_at'])
                    )
                    objects[model_name][pk] = obj

                elif model_name == 'hr.contract':
                    obj = Contract(
                        id=pk,
                        employee=objects['hr.employee'].get(fields['employee']) if fields['employee'] else None,
                        start_date=parse_date(fields['start_date']),
                        end_date=parse_date(fields['end_date']),
                        contract_type=objects['hr.contracttype'][fields['contract_type']],
                        created_at=parse_datetime(fields['created_at']),
                        updated_at=parse_datetime(fields['updated_at'])
                    )
                    obj.save()
                    objects[model_name][pk] = obj

                elif model_name == 'hr.child':
                    obj = Child.objects.create(
                        id=pk,
                        name=fields['name'],
                        gender=fields['gender'],
                        birth_date=parse_date(fields['birth_date']),
                        is_scolarise=fields['is_scolarise'],
                        created_at=parse_datetime(fields['created_at']),
                        updated_at=parse_datetime(fields['updated_at'])
                    )
                    objects[model_name][pk] = obj

                elif model_name == 'hr.employee':
                    obj = Employee(
                        id=pk,
                        employee_id=fields['employee_id'],
                        national_id=fields['national_id'],
                        full_name=fields['full_name'],
                        birth_date=parse_date(fields['birth_date']),
                        photo=fields['photo'],
                        marital_status=fields['marital_status'],
                        gender=fields['gender'],
                        email=fields['email'],
                        personal_phone=fields['personal_phone'],
                        work_phone=fields['work_phone'],
                        personal_address=fields['personal_address'],
                        work_address=fields['work_address'],
                        children_count=fields['children_count'],
                        status=fields['status'],
                        position=objects['hr.position'].get(fields['position']),
                        department=objects['hr.department'].get(fields['department']),
                        speciality=objects['hr.speciality'].get(fields['speciality']) if fields['speciality'] else None,
                        work_certificate=fields['work_certificate'],
                        legalized_contract=fields['legalized_contract'],
                        doctor_agreement=fields['doctor_agreement'],
                        temporary_agreement=fields['temporary_agreement'],
                        base_salary=Decimal(fields['base_salary']),
                        model_calcul=objects['hr.modelcalcul'].get(fields['model_calcul']),
                        career_evolution=fields['career_evolution'],
                        skills=fields['skills'],
                        is_supervisor=fields['is_supervisor'],
                        supervisor=objects['hr.employee'].get(fields['supervisor']) if fields['supervisor'] else None
                    )
                    obj.save()
                    for child_id in fields['children']:
                        obj.children.add(objects['hr.child'][child_id])
                    objects[model_name][pk] = obj

                elif model_name == 'hr.socialcontribution':
                    obj = SocialContribution.objects.create(
                        id=pk,
                        label=fields['label'],
                        rate=Decimal(fields['rate']) if fields['rate'] else None,
                        ceiling=Decimal(fields['ceiling']) if fields['ceiling'] else None
                    )
                    objects[model_name][pk] = obj

                elif model_name == 'hr.prime':
                    obj = Prime.objects.create(
                        id=pk,
                        libelle=fields['libelle'],
                        rate=Decimal(fields['rate']) if fields['rate'] else None,
                        amount=Decimal(fields['amount']) if fields['amount'] else None
                    )
                    objects[model_name][pk] = obj

                elif model_name == 'hr.modelcalcul':
                    obj = ModelCalcul.objects.create(
                        id=pk,
                        libelle=fields['libelle']
                    )
                    for sc_id in fields['social_contributions']:
                        obj.social_contributions.add(objects['hr.socialcontribution'][sc_id])
                    for prime_id in fields['primes']:
                        obj.primes.add(objects['hr.prime'][prime_id])
                    objects[model_name][pk] = obj

                elif model_name == 'hr.speciality':
                    obj = Speciality.objects.create(
                        id=pk,
                        name=fields['name']
                    )
                    objects[model_name][pk] = obj

                elif model_name == 'hr.leavetype':
                    obj = LeaveType.objects.create(
                        type_id=pk,
                        name=fields['name'],
                        default_days=Decimal(fields['default_days']) if fields['default_days'] else None,
                        accrual_method=fields['accrual_method'],
                        year=fields['year'],
                        active=fields['active'],
                        monday=fields['monday'],
                        tuesday=fields['tuesday'],
                        wednesday=fields['wednesday'],
                        thursday=fields['thursday'],
                        friday=fields['friday'],
                        saturday=fields['saturday'],
                        sunday=fields['sunday'],
                        description=fields['description']
                    )
                    objects[model_name][pk] = obj

                elif model_name == 'hr.leavebalance':
                    obj = LeaveBalance.objects.create(
                        balance_id=pk,
                        employee=objects['hr.employee'][fields['employee']],
                        leave_type=objects['hr.leavetype'][fields['leave_type']],
                        year=fields['year'],
                        entitlement=Decimal(fields['entitlement']),
                        taken=Decimal(fields['taken']),
                        remaining=Decimal(fields['remaining'])
                    )
                    objects[model_name][pk] = obj

                elif model_name == 'hr.payrollgenerationhistory':
                    obj = PayrollGenerationHistory.objects.create(
                        id=pk,
                        employee=objects['hr.employee'][fields['employee']],
                        generated_by=None,
                        generated_at=parse_datetime(fields['generated_at']),
                        start_date=parse_date(fields['start_date']),
                        end_date=parse_date(fields['end_date'])
                    )
                    objects[model_name][pk] = obj

                print(f"Créé {model_name} avec pk={pk}")

            except Exception as e:
                print(f"Erreur lors de la création de {model_name} avec pk={pk}: {str(e)}")
                raise

        print("Données insérées avec succès.")

if __name__ == '__main__':
    main()