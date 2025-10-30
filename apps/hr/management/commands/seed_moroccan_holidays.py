import sys
from datetime import date
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Seed Moroccan public holidays for a given Gregorian year into hr_holiday'

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int, default=date.today().year, help='Gregorian year to seed')
        parser.add_argument('--dry-run', action='store_true', help='Only show what would be created')

    def handle(self, *args, **options):
        from apps.hr.models.holiday import Holiday

        target_year = options['year']
        dry_run = options['dry_run']

        fixed_holidays = [
            (date(target_year, 1, 1), "Nouvel An"),
            (date(target_year, 1, 11), "Manifeste de l'Indépendance"),
            (date(target_year, 5, 1), "Fête du Travail"),
            (date(target_year, 7, 30), "Fête du Trône"),
            (date(target_year, 8, 14), "Allégeance Oued Eddahab"),
            (date(target_year, 8, 20), "Révolution du Roi et du Peuple"),
            (date(target_year, 8, 21), "Fête de la Jeunesse"),
            (date(target_year, 11, 6), "Marche Verte"),
            (date(target_year, 11, 18), "Fête de l'Indépendance"),
        ]

        islamic_holidays = []
        # Try to compute Islamic holidays using hijri-converter if available
        try:
            from hijri_converter import Gregorian, Hijri

            # Determine hijri years overlapping the Gregorian year
            hijri_start_year = Gregorian(target_year, 1, 1).to_hijri().year
            hijri_end_year = Gregorian(target_year, 12, 31).to_hijri().year

            for hyear in range(min(hijri_start_year, hijri_end_year) - 1, max(hijri_start_year, hijri_end_year) + 2):
                # 1 Muharram (Islamic New Year)
                islamic_holidays.append((Hijri(hyear, 1, 1).to_gregorian().datetimedate, "Nouvel An de l'Hégire"))
                # 10 Muharram (Achoura)
                islamic_holidays.append((Hijri(hyear, 1, 10).to_gregorian().datetimedate, "Achoura"))
                # 12 Rabi' al-awwal (Mawlid)
                islamic_holidays.append((Hijri(hyear, 3, 12).to_gregorian().datetimedate, "Naissance du Prophète"))
                # Aid al-Fitr: 1-2 Shawwal
                islamic_holidays.append((Hijri(hyear, 10, 1).to_gregorian().datetimedate, "Aïd al-Fitr"))
                islamic_holidays.append((Hijri(hyear, 10, 2).to_gregorian().datetimedate, "Aïd al-Fitr (2e jour)"))
                # Aid al-Adha: 10-11 Dhu al-Hijjah
                islamic_holidays.append((Hijri(hyear, 12, 10).to_gregorian().datetimedate, "Aïd al-Adha"))
                islamic_holidays.append((Hijri(hyear, 12, 11).to_gregorian().datetimedate, "Aïd al-Adha (2e jour)"))

            # Keep only those that fall within the Gregorian target_year
            islamic_holidays = [
                (d, n) for (d, n) in islamic_holidays if d.year == target_year
            ]
        except Exception:
            self.stdout.write(self.style.WARNING(
                "Module 'hijri_converter' non disponible ou conversion échouée. Les jours fériés islamiques ne seront pas insérés."
            ))

        to_create = []
        # Deduplicate by date+name
        seen = set()
        for d, n in fixed_holidays + islamic_holidays:
            key = (d, n)
            if key in seen:
                continue
            seen.add(key)
            # Skip if already exists
            if Holiday.objects.filter(date=d, name=n).exists():
                continue
            to_create.append(Holiday(date=d, name=n))

        if not to_create:
            self.stdout.write(self.style.SUCCESS(f"Aucun nouveau jour férié à créer pour {target_year}."))
            return

        if dry_run:
            for obj in to_create:
                self.stdout.write(f"[DRY-RUN] {obj.date} - {obj.name}")
            self.stdout.write(self.style.SUCCESS(f"{len(to_create)} éléments seraient créés."))
            return

        with transaction.atomic():
            Holiday.objects.bulk_create(to_create)

        self.stdout.write(self.style.SUCCESS(f"{len(to_create)} jours fériés insérés pour {target_year}."))


