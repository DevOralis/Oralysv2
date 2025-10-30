from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from datetime import datetime
import json

from apps.hosting.models import (
    RoomType, Room, BedStatus, Bed, Admission, Reservation, Companion
)
from apps.patient.models import Patient

# Données JSON 
data = [
    {"model": "hosting.roomtype", "pk": 1, "fields": {"name": "Single", "description": "single room", "is_active": True}}, 
    {"model": "hosting.roomtype", "pk": 2, "fields": {"name": "Double", "description": "Double Room", "is_active": True}}, 
    {"model": "hosting.roomtype", "pk": 3, "fields": {"name": "VIP", "description": "Vip Room", "is_active": True}}, 
    {"model": "hosting.room", "pk": "CH-001", "fields": {"room_name": "1", "room_type": 1, "capacity": 2, "status": "available", "description": "as"}}, 
    {"model": "hosting.room", "pk": "CH-002", "fields": {"room_name": "5", "room_type": 1, "capacity": 5, "status": "available", "description": "djhd"}}, 
    {"model": "hosting.bedstatus", "pk": 1, "fields": {"name": "Disponible"}}, 
    {"model": "hosting.bedstatus", "pk": 2, "fields": {"name": "Occupé"}}, 
    {"model": "hosting.bedstatus", "pk": 3, "fields": {"name": "Réservé"}}, 
    {"model": "hosting.bedstatus", "pk": 4, "fields": {"name": "Maintenance"}}, 
    {"model": "hosting.bed", "pk": "LIT-001", "fields": {"room": "CH-001", "bed_number": "2", "bed_status": 1}}, 
    {"model": "hosting.bed", "pk": "LIT-003", "fields": {"room": "CH-001", "bed_number": "4", "bed_status": 1}}, 
    {"model": "hosting.admission", "pk": 2, "fields": {"patient": 35, "consultation": 23, "admission_date": "2025-08-01", "assignment_mode": "bed", "room": "CH-001", "bed": "LIT-001", "room_type": "1", "discharge_date": "2025-08-31", "discharge_reason": "end_of_stay", "notes": "xvzv", "is_invoiced": False, "created_at": "2025-08-25T14:38:43.306Z"}}, 
    {"model": "hosting.reservation", "pk": 3, "fields": {"patient": 35, "room": "CH-001", "bed": "LIT-001", "start_date": "2025-08-01", "end_date": "2025-08-31", "reservation_status": "confirmed"}}, 
    {"model": "hosting.companion", "pk": 3, "fields": {"patient": 35, "companion_name": "KHALID", "relationship": "parent", "start_date": "2025-08-01", "end_date": "2025-08-31", "room": "CH-001", "bed": "LIT-001", "accommodation_start_date": "2025-08-01", "accommodation_end_date": "2025-08-31", "notes": "accompagnant"}}
]

def parse_datetime(date_str):
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    return None

def parse_date(date_str):
    if date_str:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    return None

objects = {
    'hosting.roomtype': {},
    'hosting.room': {},
    'hosting.bedstatus': {},
    'hosting.bed': {},
    'hosting.admission': {},
    'hosting.reservation': {},
    'hosting.companion': {}
}

class Command(BaseCommand):
    help = 'Populates the hosting database with initial data'

    def add_arguments(self, parser):
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
                if model_name == 'hosting.roomtype':
                    obj = RoomType.objects.create(
                        id=pk,
                        name=fields['name'],
                        description=fields['description'],
                        is_active=fields['is_active']
                    )
                    objects[model_name][pk] = obj

                elif model_name == 'hosting.room':
                    obj = Room.objects.create(
                        room_id=pk,
                        room_name=fields['room_name'],
                        room_type=objects['hosting.roomtype'][fields['room_type']],
                        capacity=fields['capacity'],
                        status=fields['status'],
                        description=fields['description']
                    )
                    objects[model_name][pk] = obj

                elif model_name == 'hosting.bedstatus':
                    obj = BedStatus.objects.create(
                        id=pk,
                        name=fields['name']
                    )
                    objects[model_name][pk] = obj

                elif model_name == 'hosting.bed':
                    obj = Bed.objects.create(
                        bed_id=pk,
                        room=objects['hosting.room'][fields['room']],
                        bed_number=fields['bed_number'],
                        bed_status=objects['hosting.bedstatus'][fields['bed_status']]
                    )
                    objects[model_name][pk] = obj

                elif model_name == 'hosting.admission':
                    try:
                        patient = Patient.objects.get(pk=fields['patient'])
                    except Patient.DoesNotExist:
                        print(f"⚠️  Admission ignorée - pk={pk} (patient_id={fields['patient']} n'existe pas)")
                        continue
                        
                    obj = Admission.objects.create(
                        id=pk,
                        patient=patient,
                        admission_date=parse_date(fields['admission_date']),
                        assignment_mode=fields['assignment_mode'],
                        room=objects['hosting.room'][fields['room']] if fields.get('room') else None,
                        bed=objects['hosting.bed'][fields['bed']] if fields.get('bed') else None,
                        room_type=fields.get('room_type'),
                        discharge_date=parse_date(fields['discharge_date']) if fields.get('discharge_date') else None,
                        discharge_reason=fields.get('discharge_reason'),
                        notes=fields.get('notes', ''),
                        is_invoiced=fields.get('is_invoiced', False),
                        created_at=parse_datetime(fields['created_at']) if fields.get('created_at') else None
                    )
                    objects[model_name][pk] = obj

                elif model_name == 'hosting.reservation':
                    try:
                        patient = Patient.objects.get(pk=fields['patient'])
                    except Patient.DoesNotExist:
                        print(f"⚠️  Réservation ignorée - pk={pk} (patient_id={fields['patient']} n'existe pas)")
                        continue
                        
                    obj = Reservation.objects.create(
                        id=pk,
                        patient=patient,
                        room=objects['hosting.room'][fields['room']],
                        bed=objects['hosting.bed'][fields['bed']] if fields.get('bed') else None,
                        start_date=parse_date(fields['start_date']),
                        end_date=parse_date(fields['end_date']),
                        reservation_status=fields['reservation_status']
                    )
                    objects[model_name][pk] = obj

                elif model_name == 'hosting.companion':
                    try:
                        patient = Patient.objects.get(pk=fields['patient'])
                    except Patient.DoesNotExist:
                        print(f"⚠️  Companion ignoré - pk={pk} (patient_id={fields['patient']} n'existe pas)")
                        continue
                        
                    obj = Companion.objects.create(
                        id=pk,
                        patient=patient,
                        companion_name=fields['companion_name'],
                        relationship=fields['relationship'],
                        start_date=parse_date(fields['start_date']),
                        end_date=parse_date(fields['end_date']) if fields.get('end_date') else None,
                        room=objects['hosting.room'][fields['room']] if fields.get('room') else None,
                        bed=objects['hosting.bed'][fields['bed']] if fields.get('bed') else None,
                        accommodation_start_date=parse_date(fields['accommodation_start_date']) if fields.get('accommodation_start_date') else None,
                        accommodation_end_date=parse_date(fields['accommodation_end_date']) if fields.get('accommodation_end_date') else None,
                        notes=fields.get('notes', '')
                    )
                    objects[model_name][pk] = obj

                self.stdout.write(self.style.SUCCESS(f"Créé {model_name} avec pk={pk}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erreur lors de la création de {model_name} avec pk={pk}: {str(e)}"))
                raise

        self.stdout.write(self.style.SUCCESS('Données hosting insérées avec succès.'))
