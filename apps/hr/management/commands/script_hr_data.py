
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.files import File
from decimal import Decimal
from datetime import datetime
import os
import json

from apps.hr.models import (
    Department, Position, ContractType, Contract, Child, Employee,
    SocialContribution, Prime, ModelCalcul, Speciality, LeaveType,
    LeaveBalance, PayrollGenerationHistory, MedicalVisit
)

# Données JSON 
data = [
  {"model": "hr.department", "pk": 1, "fields": {"name": "Administration", "description": "None", "parent": "None", "created_at": "2025-08-20T22:04:36.078Z", "updated_at": "2025-08-20T22:04:36.078Z"}},
  {"model": "hr.department", "pk": 2, "fields": {"name": "Urgences", "description": "None", "parent": "None", "created_at": "2025-08-20T22:04:36.081Z", "updated_at": "2025-08-20T22:04:36.081Z"}},
  {"model": "hr.department", "pk": 3, "fields": {"name": "Pédiatrie", "description": "None", "parent": "None", "created_at": "2025-08-20T22:04:36.082Z", "updated_at": "2025-08-20T22:04:36.082Z"}},
  {"model": "hr.department", "pk": 4, "fields": {"name": "Pharmacie", "description": "None", "parent": "None", "created_at": "2025-08-20T22:04:36.083Z", "updated_at": "2025-08-20T22:04:36.083Z"}},
  {"model": "hr.department", "pk": 6, "fields": {"name": "Ressources Humaines", "description": "None", "parent": 1, "created_at": "2025-08-20T22:04:36.084Z", "updated_at": "2025-08-20T22:04:36.084Z"}},
  {"model": "hr.department", "pk": 8, "fields": {"name": "ActivitÃ©s ThÃ©rapeutiques", "description": "DÃ©partement des activitÃ©s thÃ©rapeutiques et paramÃ©dicales", "parent": "None", "created_at": "2025-08-23T07:44:14.157Z", "updated_at": "2025-08-23T07:44:14.157Z"}},
  {"model": "hr.position", "pk": 1, "fields": {"name": "Infirmiere", "description": "None", "created_at": "2025-08-20T22:04:36.084Z", "updated_at": "2025-08-20T22:04:36.084Z"}},
  {"model": "hr.position", "pk": 2, "fields": {"name": "Ressources Humaines", "description": "None", "created_at": "2025-08-20T22:04:36.086Z", "updated_at": "2025-08-20T22:04:36.086Z"}},
  {"model": "hr.position", "pk": 3, "fields": {"name": "Médecin ", "description": "None", "created_at": "2025-08-20T22:04:36.087Z", "updated_at": "2025-08-20T22:04:36.087Z"}},
  {"model": "hr.position", "pk": 4, "fields": {"name": "Médecin Vacataire", "description": "None", "created_at": "2025-08-20T22:04:36.088Z", "updated_at": "2025-08-20T22:04:36.088Z"}},
  {"model": "hr.position", "pk": 5, "fields": {"name": "Secrétaire", "description": "None", "created_at": "2025-08-20T22:04:36.089Z", "updated_at": "2025-08-20T22:04:36.089Z"}},
  {"model": "hr.position", "pk": 6, "fields": {"name": "Technicien", "description": "None", "created_at": "2025-08-20T22:04:36.091Z", "updated_at": "2025-08-20T22:04:36.091Z"}},
  {"model": "hr.position", "pk": 18, "fields": {"name": "Coach", "description": "None", "created_at": "2025-08-20T22:04:36.091Z", "updated_at": "2025-08-20T22:04:36.091Z"}},
  {"model": "hr.contracttype", "pk": 1, "fields": {"name": "CDD", "description": "None", "created_at": "2025-08-20T22:04:36.093Z", "updated_at": "2025-08-20T22:04:36.093Z"}},
  {"model": "hr.contracttype", "pk": 2, "fields": {"name": "CDI", "description": "None", "created_at": "2025-08-20T22:04:36.095Z", "updated_at": "2025-08-20T22:04:36.095Z"}},
  {"model": "hr.contracttype", "pk": 3, "fields": {"name": "ANAPEC", "description": "None", "created_at": "2025-08-20T22:04:36.095Z", "updated_at": "2025-08-20T22:04:36.095Z"}},
  {"model": "hr.contract", "pk": 21, "fields": {"employee": "None", "start_date": "2025-07-30", "end_date": "None", "contract_type": 3, "created_at": "2025-08-20T22:04:36.108Z", "updated_at": "2025-08-20T22:04:36.108Z"}},
  {"model": "hr.contract", "pk": 22, "fields": {"employee": "None", "start_date": "2025-07-01", "end_date": "None", "contract_type": 3, "created_at": "2025-08-20T22:04:36.116Z", "updated_at": "2025-08-20T22:04:36.116Z"}},
  {"model": "hr.contract", "pk": 24, "fields": {"employee": "None", "start_date": "2025-08-22", "end_date": "None", "contract_type": 2, "created_at": "2025-08-20T22:04:36.120Z", "updated_at": "2025-08-20T22:04:36.120Z"}},
  {"model": "hr.contract", "pk": 25, "fields": {"employee": "None", "start_date": "2025-08-26", "end_date": "None", "contract_type": 3, "created_at": "2025-08-20T22:04:36.124Z", "updated_at": "2025-08-20T22:04:36.124Z"}},
  {"model": "hr.contract", "pk": 26, "fields": {"employee": "None", "start_date": "2025-08-26", "end_date": "2025-08-25", "contract_type": 1, "created_at": "2025-08-20T22:04:36.126Z", "updated_at": "2025-08-20T22:04:36.126Z"}},
  {"model": "hr.contract", "pk": 27, "fields": {"employee": "None", "start_date": "2025-08-27", "end_date": "None", "contract_type": 3, "created_at": "2025-08-20T22:04:36.129Z", "updated_at": "2025-08-20T22:04:36.129Z"}},
  {"model": "hr.contract", "pk": 28, "fields": {"employee": "None", "start_date": "2025-08-26", "end_date": "2025-08-28", "contract_type": 1, "created_at": "2025-08-20T22:04:36.131Z", "updated_at": "2025-08-20T22:04:36.131Z"}},
  {"model": "hr.contract", "pk": 30, "fields": {"employee": 4, "start_date": "2025-08-21", "end_date": "None", "contract_type": 3, "created_at": "2025-08-20T22:11:22.737Z", "updated_at": "2025-08-25T16:00:31.217Z"}},
  {"model": "hr.contract", "pk": 31, "fields": {"employee": 16, "start_date": "2025-08-02", "end_date": "2025-08-17", "contract_type": 1, "created_at": "2025-08-25T16:00:45.663Z", "updated_at": "2025-08-25T16:00:45.663Z"}},
  {"model": "hr.contract", "pk": 32, "fields": {"employee": 12, "start_date": "2025-08-28", "end_date": "None", "contract_type": 3, "created_at": "2025-08-25T16:00:56.738Z", "updated_at": "2025-08-25T16:00:56.739Z"}},
  {"model": "hr.contract", "pk": 33, "fields": {"employee": 14, "start_date": "2025-08-20", "end_date": "None", "contract_type": 3, "created_at": "2025-08-25T16:01:07.750Z", "updated_at": "2025-08-25T16:01:07.750Z"}},
  {"model": "hr.contract", "pk": 34, "fields": {"employee": 15, "start_date": "2025-08-21", "end_date": "None", "contract_type": 2, "created_at": "2025-08-25T16:01:18.688Z", "updated_at": "2025-08-25T16:01:18.688Z"}},
  {"model": "hr.child", "pk": 73, "fields": {"name": "Ennhili yassine", "gender": "M", "birth_date": "2025-08-28", "is_scolarise": True, "created_at": "2025-08-20T22:04:36.135Z", "updated_at": "2025-08-20T22:04:36.135Z"}},
  {"model": "hr.child", "pk": 76, "fields": {"name": "HIND", "gender": "F", "birth_date": "2025-08-29", "is_scolarise": True, "created_at": "2025-08-20T22:04:36.140Z", "updated_at": "2025-08-20T22:04:36.140Z"}},
  {"model": "hr.child", "pk": 81, "fields": {"name": "omar omar", "gender": "M", "birth_date": "2025-08-07", "is_scolarise": True, "created_at": "2025-08-20T22:04:36.142Z", "updated_at": "2025-08-20T22:04:36.142Z"}},
  {"model": "hr.child", "pk": 82, "fields": {"name": "yassi neennhili", "gender": "M", "birth_date": "2025-08-27", "is_scolarise": True, "created_at": "2025-08-20T22:04:36.144Z", "updated_at": "2025-08-20T22:04:36.144Z"}},
  {"model": "hr.child", "pk": 84, "fields": {"name": "Kawtar Berrouch", "gender": "M", "birth_date": "2025-08-28", "is_scolarise": True, "created_at": "2025-08-20T22:13:01.216Z", "updated_at": "2025-08-20T22:13:01.216Z"}},
  {"model": "hr.child", "pk": 85, "fields": {"name": "OUALID", "gender": "M", "birth_date": "None", "is_scolarise": False, "created_at": "2025-08-20T22:13:43.611Z", "updated_at": "2025-08-20T22:13:43.611Z"}},
  {"model": "hr.child", "pk": 86, "fields": {"name": "yassi neennhili", "gender": "M", "birth_date": "None", "is_scolarise": False, "created_at": "2025-08-20T22:13:43.614Z", "updated_at": "2025-08-20T22:13:43.614Z"}},
  {"model": "hr.child", "pk": 87, "fields": {"name": "yassi neennhili", "gender": "M", "birth_date": "None", "is_scolarise": False, "created_at": "2025-08-25T16:00:31.195Z", "updated_at": "2025-08-25T16:00:31.195Z"}},
  {"model": "hr.child", "pk": 88, "fields": {"name": "Kawtar Berrouch", "gender": "M", "birth_date": "2025-08-28", "is_scolarise": True, "created_at": "2025-08-25T16:00:45.642Z", "updated_at": "2025-08-25T16:00:45.642Z"}},
  {"model": "hr.child", "pk": 89, "fields": {"name": "omar omar", "gender": "M", "birth_date": "2025-08-07", "is_scolarise": True, "created_at": "2025-08-25T16:00:56.691Z", "updated_at": "2025-08-25T16:00:56.691Z"}},
  {"model": "hr.child", "pk": 90, "fields": {"name": "yassi neennhili", "gender": "M", "birth_date": "2025-08-27", "is_scolarise": True, "created_at": "2025-08-25T16:00:56.714Z", "updated_at": "2025-08-25T16:00:56.714Z"}},
  {"model": "hr.child", "pk": 91, "fields": {"name": "Ennhili yassine", "gender": "M", "birth_date": "2025-08-28", "is_scolarise": True, "created_at": "2025-08-25T16:01:07.712Z", "updated_at": "2025-08-25T16:01:07.712Z"}},
  {"model": "hr.child", "pk": 92, "fields": {"name": "HIND", "gender": "F", "birth_date": "2025-08-29", "is_scolarise": True, "created_at": "2025-08-25T16:01:18.651Z", "updated_at": "2025-08-25T16:01:18.651Z"}},
  {"model": "hr.socialcontribution", "pk": 2, "fields": {"label": "CNSS", "rate": "3.96", "ceiling": "6000.00"}},
  {"model": "hr.socialcontribution", "pk": 3, "fields": {"label": "AMO", "rate": "2.26", "ceiling": "0.00"}},
  {"model": "hr.socialcontribution", "pk": 5, "fields": {"label": "frais professionnelles", "rate": "20.00", "ceiling": "500.00"}},
  {"model": "hr.socialcontribution", "pk": 9, "fields": {"label": "CIMR", "rate": "3.00", "ceiling": "None"}},
  {"model": "hr.prime", "pk": 8, "fields": {"libelle": "Prime D'aciennete ", "rate": "5.00", "amount": "None"}},
  {"model": "hr.prime", "pk": 13, "fields": {"libelle": "Prime de transport ", "rate": "None", "amount": "500.00"}},
  {"model": "hr.prime", "pk": 15, "fields": {"libelle": "Prime de repas", "rate": "None", "amount": "300.00"}},
  {"model": "hr.prime", "pk": 18, "fields": {"libelle": "prime de Logement", "rate": "None", "amount": "500.00"}},
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
  {"model": "hr.employee", "pk": 4, "fields": {"employee_id": "A3", "national_id": "EE333333", "full_name": "HASSNAe erramach", "birth_date": "2025-06-29", "photo": "hr_media/employees_profile/WhatsApp_Image_2025-06-29_at_12.07.57_d0550036.jpg", "marital_status": "M", "gender": "F", "email": "hassna200@gmail.com", "personal_phone": "0733333333", "work_phone": "0733333333", "personal_address": "mabrouka", "work_address": "EC 12 ", "children_count": 1, "status": "A", "position": 18, "department": 1, "speciality": "None", "work_certificate": "", "legalized_contract": "hr_media/legalized_contracts/Résumé_COCOMO_r5XuCb8.pdf", "doctor_agreement": "", "temporary_agreement": "", "base_salary": "2300.00", "model_calcul": 4, "career_evolution": "PR HASSNA ERRAMACH", "skills": "CS", "is_supervisor": 1, "supervisor": "None", "children": [85, 86]}},
  {"model": "hr.employee", "pk": 12, "fields": {"employee_id": "A0", "national_id": "EE000000", "full_name": "Ennhili yassine", "birth_date": "2025-07-01", "photo": "hr_media/employees_profile/pillar_architecture.svg", "marital_status": "S", "gender": "M", "email": "yassinenhili2002@gmail.com", "personal_phone": "0773694763", "work_phone": "0773694763", "personal_address": "fkuyf", "work_address": "vhhk", "children_count": 1, "status": "A", "position": 3, "department": 3, "speciality": 13, "work_certificate": "", "legalized_contract": "hr_media/legalized_contracts/citeinnovation.pdf", "doctor_agreement": "hr_media/doctor_agreements/pharmacy_stock_movements_report.pdf", "temporary_agreement": "", "base_salary": "5000.00", "model_calcul": 4, "career_evolution": "agiur", "skills": "SR", "is_supervisor": 1, "supervisor": "None", "children": [81, 82]}},
  {"model": "hr.employee", "pk": 14, "fields": {"employee_id": "CLV01", "national_id": "EE010101", "full_name": "ENNHILI YASSINE", "birth_date": "2025-08-30", "photo": "", "marital_status": "S", "gender": "M", "email": "yassinenhili2002@gmail.com", "personal_phone": "0773694763", "work_phone": "0773694763", "personal_address": "fkuyf", "work_address": "vhhk", "children_count": 1, "status": "A", "position": 2, "department": 6, "speciality": "None", "work_certificate": "", "legalized_contract": "hr_media/legalized_contracts/consultation_ENNHILI_Yassine_20250809.pdf", "doctor_agreement": "", "temporary_agreement": "", "base_salary": "3900.00", "model_calcul": 6, "career_evolution": "WRE", "skills": "ADS", "is_supervisor": 1, "supervisor": "None", "children": [73]}},
  {"model": "hr.employee", "pk": 15, "fields": {"employee_id": "CLV02", "national_id": "EE010102", "full_name": "Kawtar Berrouch", "birth_date": "2025-08-05", "photo": "hr_media/employees_profile/data_pipeline.svg", "marital_status": "M", "gender": "M", "email": "yassinenhili2002@gmail.com", "personal_phone": "0773694763", "work_phone": "0773694763", "personal_address": "fkuyf", "work_address": "vhhk", "children_count": 1, "status": "A", "position": 2, "department": 6, "speciality": "None", "work_certificate": "", "legalized_contract": "hr_media/legalized_contracts/demande_prix_pharmacie_PHARM-PO-000023.pdf", "doctor_agreement": "", "temporary_agreement": "", "base_salary": "3400.00", "model_calcul": 6, "career_evolution": "", "skills": "", "is_supervisor": 0, "supervisor": 14, "children": [76]}},
  {"model": "hr.employee", "pk": 16, "fields": {"employee_id": "CLV03", "national_id": "EE030303", "full_name": "OMAR ENNHILI", "birth_date": "2025-08-01", "photo": "hr_media/employees_profile/diagnostic_ai_assistant_architecture.svg", "marital_status": "M", "gender": "M", "email": "yassinenhili2002@gmail.com", "personal_phone": "0773694763", "work_phone": "F", "personal_address": "fkuyf", "work_address": "vhhk", "children_count": 1, "status": "A", "position": 18, "department": 1, "speciality": "None", "work_certificate": "", "legalized_contract": "hr_media/legalized_contracts/Résumé_COCOMO.pdf", "doctor_agreement": "", "temporary_agreement": "", "base_salary": "35000.00", "model_calcul": 4, "career_evolution": "S", "skills": "SDY", "is_supervisor": 0, "supervisor": "None", "children": [84]}},
  {"model": "hr.employee", "pk": 18, "fields": {"employee_id": "COACH001", "national_id": "A205341", "full_name": "Mehdi Zeroual", "birth_date": "1982-04-26", "photo": "", "marital_status": "M", "gender": "M", "email": "mehdi.zeroual@oralys.ma", "personal_phone": "+2120743312873", "work_phone": "+212552386737", "personal_address": "Adresse personnelle de Mehdi Zeroual", "work_address": "Centre Oralys, Casablanca", "children_count": 2, "status": "A", "position": 18, "department": 8, "speciality": "None", "work_certificate": "", "legalized_contract": "", "doctor_agreement": "", "temporary_agreement": "", "base_salary": "18540.00", "model_calcul": "None", "career_evolution": "None", "skills": "None", "is_supervisor": 0, "supervisor": "None", "children": []}},
  {"model": "hr.employee", "pk": 19, "fields": {"employee_id": "COACH002", "national_id": "A931319", "full_name": "Sofia Cherkaoui", "birth_date": "1985-02-25", "photo": "", "marital_status": "S", "gender": "F", "email": "sofia.cherkaoui@oralys.ma", "personal_phone": "+2120690003651", "work_phone": "+212527933085", "personal_address": "Adresse personnelle de Sofia Cherkaoui", "work_address": "Centre Oralys, Casablanca", "children_count": 3, "status": "A", "position": 18, "department": 8, "speciality": "None", "work_certificate": "", "legalized_contract": "", "doctor_agreement": "", "temporary_agreement": "", "base_salary": "22451.00", "model_calcul": "None", "career_evolution": "None", "skills": "None", "is_supervisor": 0, "supervisor": "None", "children": []}},
  {"model": "hr.employee", "pk": 20, "fields": {"employee_id": "COACH003", "national_id": "A221756", "full_name": "Ahmed Bennis", "birth_date": "1974-07-17", "photo": "", "marital_status": "D", "gender": "M", "email": "ahmed.bennis@oralys.ma", "personal_phone": "+2120657484664", "work_phone": "+212556531766", "personal_address": "Adresse personnelle de Ahmed Bennis", "work_address": "Centre Oralys, Casablanca", "children_count": 2, "status": "A", "position": 18, "department": 8, "speciality": "None", "work_certificate": "", "legalized_contract": "", "doctor_agreement": "", "temporary_agreement": "", "base_salary": "22382.00", "model_calcul": "None", "career_evolution": "None", "skills": "None", "is_supervisor": 0, "supervisor": "None", "children": []}},
  {"model": "hr.employee", "pk": 21, "fields": {"employee_id": "COACH004", "national_id": "A686516", "full_name": "Amina Zeroual", "birth_date": "1997-03-05", "photo": "", "marital_status": "S", "gender": "F", "email": "amina.zeroual@oralys.ma", "personal_phone": "+2120743915384", "work_phone": "+212516083326", "personal_address": "Adresse personnelle de Amina Zeroual", "work_address": "Centre Oralys, Casablanca", "children_count": 0, "status": "A", "position": 18, "department": 8, "speciality": "None", "work_certificate": "", "legalized_contract": "", "doctor_agreement": "", "temporary_agreement": "", "base_salary": "22594.00", "model_calcul": "None", "career_evolution": "None", "skills": "None", "is_supervisor": 0, "supervisor": "None", "children": []}},
  {"model": "hr.employee", "pk": 22, "fields": {"employee_id": "COACH005", "national_id": "A359840", "full_name": "Hicham Bennis", "birth_date": "1971-12-01", "photo": "", "marital_status": "D", "gender": "M", "email": "hicham.bennis@oralys.ma", "personal_phone": "+2120606130280", "work_phone": "+212530772974", "personal_address": "Adresse personnelle de Hicham Bennis", "work_address": "Centre Oralys, Casablanca", "children_count": 1, "status": "A", "position": 18, "department": 8, "speciality": "None", "work_certificate": "", "legalized_contract": "", "doctor_agreement": "", "temporary_agreement": "", "base_salary": "21958.00", "model_calcul": "None", "career_evolution": "None", "skills": "None", "is_supervisor": 0, "supervisor": "None", "children": []}},
  {"model": "hr.employee", "pk": 23, "fields": {"employee_id": "COACH006", "national_id": "A606438", "full_name": "Amina Benjelloun", "birth_date": "1981-04-24", "photo": "", "marital_status": "M", "gender": "F", "email": "amina.benjelloun@oralys.ma", "personal_phone": "+2120757789769", "work_phone": "+212579825043", "personal_address": "Adresse personnelle de Amina Benjelloun", "work_address": "Centre Oralys, Casablanca", "children_count": 2, "status": "A", "position": 18, "department": 8, "speciality": "None", "work_certificate": "", "legalized_contract": "", "doctor_agreement": "", "temporary_agreement": "", "base_salary": "20932.00", "model_calcul": "None", "career_evolution": "None", "skills": "None", "is_supervisor": 0, "supervisor": "None", "children": []}},
  {"model": "hr.leavetype", "pk": 24, "fields": {"name": "conge maladie", "default_days": "None", "accrual_method": "annual", "year": 2024, "active": True, "monday": True, "tuesday": True, "wednesday": True, "thursday": True, "friday": True, "saturday": True, "sunday": False, "description": "merci"}},
  {"model": "hr.leavetype", "pk": 25, "fields": {"name": "Conge annuel", "default_days": "24.00", "accrual_method": "annual", "year": 2024, "active": True, "monday": True, "tuesday": True, "wednesday": True, "thursday": True, "friday": True, "saturday": False, "sunday": False, "description": "maladie"}},
  {"model": "hr.leavetype", "pk": 26, "fields": {"name": "conge exceptionnel", "default_days": "None", "accrual_method": "annual", "year": 2024, "active": True, "monday": True, "tuesday": True, "wednesday": True, "thursday": True, "friday": True, "saturday": False, "sunday": False, "description": "wqe"}},
  {"model": "hr.leavebalance", "pk": 1, "fields": {"employee": 14, "leave_type": 24, "year": 2025, "entitlement": "0.00", "taken": "0.00", "remaining": "0.00"}},
  {"model": "hr.leavebalance", "pk": 2, "fields": {"employee": 15, "leave_type": 24, "year": 2025, "entitlement": "0.00", "taken": "0.00", "remaining": "0.00"}},
  {"model": "hr.leavebalance", "pk": 3, "fields": {"employee": 12, "leave_type": 24, "year": 2025, "entitlement": "0.00", "taken": "0.00", "remaining": "0.00"}},
  {"model": "hr.leavebalance", "pk": 4, "fields": {"employee": 12, "leave_type": 26, "year": 2025, "entitlement": "0.00", "taken": "0.00", "remaining": "0.00"}},
  {"model": "hr.leavebalance", "pk": 5, "fields": {"employee": 15, "leave_type": 25, "year": 2025, "entitlement": "24.00", "taken": "6.00", "remaining": "18.00"}},
  {"model": "hr.leavebalance", "pk": 6, "fields": {"employee": 16, "leave_type": 26, "year": 2025, "entitlement": "0.00", "taken": "0.00", "remaining": "0.00"}},
  {"model": "hr.leavebalance", "pk": 7, "fields": {"employee": 15, "leave_type": 26, "year": 2025, "entitlement": "0.00", "taken": "0.00", "remaining": "0.00"}},
  {"model": "hr.leavebalance", "pk": 8, "fields": {"employee": 14, "leave_type": 25, "year": 2025, "entitlement": "24.00", "taken": "3.00", "remaining": "21.00"}},
  {"model": "hr.leavebalance", "pk": 9, "fields": {"employee": 14, "leave_type": 26, "year": 2025, "entitlement": "0.00", "taken": "0.00", "remaining": "0.00"}},
  {"model": "hr.leavebalance", "pk": 50, "fields": {"employee": 4, "leave_type": 26, "year": 2025, "entitlement": "0.00", "taken": "0.00", "remaining": "0.00"}},
  {"model": "hr.leavebalance", "pk": 51, "fields": {"employee": 4, "leave_type": 25, "year": 2025, "entitlement": "24.00", "taken": "5.00", "remaining": "19.00"}},
  {"model": "hr.leavebalance", "pk": 53, "fields": {"employee": 4, "leave_type": 24, "year": 2025, "entitlement": "0.00", "taken": "0.00", "remaining": "0.00"}},
  {"model": "hr.payrollgenerationhistory", "pk": 1, "fields": {"employee": 14, "generated_by": "None", "generated_at": "2025-08-20T21:40:44.641Z", "start_date": "2025-08-07", "end_date": "2025-08-29"}},
  {"model": "hr.payrollgenerationhistory", "pk": 2, "fields": {"employee": 12, "generated_by": "None", "generated_at": "2025-08-20T21:40:44.649Z", "start_date": "2025-08-05", "end_date": "2025-09-07"}},
  {"model": "hr.payrollgenerationhistory", "pk": 13, "fields": {"employee": 12, "generated_by": "None", "generated_at": "2025-08-20T21:40:44.651Z", "start_date": "2025-07-01", "end_date": "2025-07-31"}},
  {"model": "hr.medicalvisit", "pk": 2, "fields": {"employee": 14, "doctor_name": "Ennhili yassine", "visit_date": "2025-08-26", "result_file": "hr_media/medical_results/demande_prix_pharmacie_PHARM-PO-000023_sOgvrDC.pdf", "created_at": "2025-08-20T21:40:44.652Z", "updated_at": "2025-08-25T16:01:07.738Z"}},
  {"model": "hr.medicalvisit", "pk": 4, "fields": {"employee": 4, "doctor_name": "Ennhili yassine", "visit_date": "2025-08-12", "result_file": "hr_media/medical_results/Automated_MCQ_Grading_Using_AI_A_Dual-Approach_Web-Based_Soluti_tsgkjgM.pdf", "created_at": "2025-08-20T21:40:44.658Z", "updated_at": "2025-08-25T16:00:31.210Z"}},
  {"model": "hr.medicalvisit", "pk": 5, "fields": {"employee": 15, "doctor_name": "Ennhili yassine", "visit_date": "2025-08-28", "result_file": "hr_media/medical_results/pharmacy_adjustment_20250806.pdf", "created_at": "2025-08-20T21:40:44.661Z", "updated_at": "2025-08-25T16:01:18.681Z"}},
  {"model": "hr.medicalvisit", "pk": 6, "fields": {"employee": 16, "doctor_name": "Ennhili yassine", "visit_date": "2025-08-28", "result_file": "hr_media/medical_results/pharmacy_stock_movements_report.pdf", "created_at": "2025-08-20T21:40:44.663Z", "updated_at": "2025-08-25T16:00:45.655Z"}}
]


def parse_datetime(date_str):
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            # Fallback when microseconds are absent or have fewer digits
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    return None

def parse_date(date_str):
    if date_str:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    return None

def clean_none_values(value):
    """Convertit les chaînes 'None' en vraies valeurs None"""
    if value == "None" or value is None or value == "" or value == "null":
        return None
    return value

def is_null_value(value):
    """Vérifie si une valeur est considérée comme null"""
    return value is None or value == "None" or value == "" or value == "null" or str(value).strip() == ""

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
    'hr.payrollgenerationhistory': {},
    'hr.medicalvisit': {}
}

class Command(BaseCommand):
    help = 'Populates the HR database with initial data'

    def add_arguments(self, parser):
        # Chemin optionnel vers le fichier JSON exporté via `python manage.py dumpdata hr`
        parser.add_argument('json_file', type=str, nargs='?', help='Path to dumpdata JSON file')

    @transaction.atomic
    def handle(self, *args, **options):
        json_file = options.get('json_file')
        if json_file:
            with open(json_file, 'r', encoding='utf-8') as jf:
                loaded_data = json.load(jf)
        else:
            loaded_data = data

        for item in loaded_data:
            model_name = item['model']
            pk = item['pk']
            fields = item['fields']

            try:
                if model_name == 'hr.department':
                    obj = Department.objects.create(
                        id=pk,
                        name=fields['name'],
                        description=clean_none_values(fields['description']),
                        parent_id=clean_none_values(fields['parent']),
                        created_at=parse_datetime(fields['created_at']),
                        updated_at=parse_datetime(fields['updated_at'])
                    )
                    objects[model_name][pk] = obj

                elif model_name == 'hr.position':
                    obj = Position.objects.create(
                        id=pk,
                        name=fields['name'],
                        description=clean_none_values(fields['description']),
                        created_at=parse_datetime(fields['created_at']),
                        updated_at=parse_datetime(fields['updated_at'])
                    )
                    objects[model_name][pk] = obj

                elif model_name == 'hr.contracttype':
                    obj = ContractType.objects.create(
                        id=pk,
                        name=fields['name'],
                        description=clean_none_values(fields['description']),
                        created_at=parse_datetime(fields['created_at']),
                        updated_at=parse_datetime(fields['updated_at'])
                    )
                    objects[model_name][pk] = obj

                elif model_name == 'hr.contract':
                    employee_id = clean_none_values(fields['employee'])
                    end_date = clean_none_values(fields['end_date'])
                    
                    # Ignorer les contrats orphelins (sans employee_id)
                    if is_null_value(fields['employee']):
                        print(f"⚠️  Contrat orphelin ignoré - pk={pk} (employee_id={fields['employee']})")
                        continue
                    
                    # Vérifier que l'employé existe
                    employee = objects['hr.employee'].get(employee_id)
                    if not employee:
                        print(f"⚠️  Contrat ignoré - pk={pk} (employee_id={employee_id} n'existe pas)")
                        continue
                        
                    obj = Contract(
                        id=pk,
                        employee=employee,
                        start_date=parse_date(fields['start_date']),
                        end_date=parse_date(end_date) if end_date else None,
                        contract_type=objects['hr.contracttype'][fields['contract_type']],
                        created_at=parse_datetime(fields['created_at']),
                        updated_at=parse_datetime(fields['updated_at'])
                    )
                    obj.save()
                    objects[model_name][pk] = obj

                elif model_name == 'hr.child':
                    birth_date = clean_none_values(fields['birth_date'])
                    obj = Child.objects.create(
                        id=pk,
                        name=fields['name'],
                        gender=fields['gender'],
                        birth_date=parse_date(birth_date) if birth_date else None,
                        is_scolarise=fields['is_scolarise'],
                        created_at=parse_datetime(fields['created_at']),
                        updated_at=parse_datetime(fields['updated_at'])
                    )
                    objects[model_name][pk] = obj

                elif model_name == 'hr.employee':
                    speciality = clean_none_values(fields['speciality'])
                    model_calcul = clean_none_values(fields['model_calcul'])
                    supervisor = clean_none_values(fields['supervisor'])
                    career_evolution = clean_none_values(fields['career_evolution'])
                    skills = clean_none_values(fields['skills'])
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
                        speciality=objects['hr.speciality'].get(speciality) if speciality else None,
                        work_certificate=fields['work_certificate'],
                        legalized_contract=fields['legalized_contract'],
                        doctor_agreement=fields['doctor_agreement'],
                        temporary_agreement=fields['temporary_agreement'],
                        base_salary=Decimal(fields['base_salary']),
                        model_calcul=objects['hr.modelcalcul'].get(model_calcul) if model_calcul else None,
                        career_evolution=career_evolution,
                        skills=skills,
                        is_supervisor=fields['is_supervisor'],
                        supervisor=objects['hr.employee'].get(supervisor) if supervisor else None
                    )
                    obj.save()
                    for child_id in fields['children']:
                        obj.children.add(objects['hr.child'][child_id])
                    objects[model_name][pk] = obj

                elif model_name == 'hr.socialcontribution':
                    rate = clean_none_values(fields['rate'])
                    ceiling = clean_none_values(fields['ceiling'])
                    obj = SocialContribution.objects.create(
                        id=pk,
                        label=fields['label'],
                        rate=Decimal(rate) if rate else None,
                        ceiling=Decimal(ceiling) if ceiling else None
                    )
                    objects[model_name][pk] = obj

                elif model_name == 'hr.prime':
                    rate = clean_none_values(fields['rate'])
                    amount = clean_none_values(fields['amount'])
                    obj = Prime.objects.create(
                        id=pk,
                        libelle=fields['libelle'],
                        rate=Decimal(rate) if rate else None,
                        amount=Decimal(amount) if amount else None
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
                    default_days = clean_none_values(fields['default_days'])
                    description = clean_none_values(fields['description'])
                    obj = LeaveType.objects.create(
                        type_id=pk,
                        name=fields['name'],
                        default_days=Decimal(default_days) if default_days else None,
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
                        description=description
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

                elif model_name == 'hr.medicalvisit':
                    obj = MedicalVisit.objects.create(
                        id=pk,
                        employee=objects['hr.employee'][fields['employee']],
                        doctor_name=fields['doctor_name'],
                        visit_date=parse_date(fields['visit_date']),
                        result_file=fields['result_file']
                    )
                    objects[model_name][pk] = obj

                self.stdout.write(self.style.SUCCESS(f"Créé {model_name} avec pk={pk}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erreur lors de la création de {model_name} avec pk={pk}: {str(e)}"))
                raise

        self.stdout.write(self.style.SUCCESS('Données insérées avec succès.'))