from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed a default HR admin user with full access"

    def handle(self, *args, **options):
        # Code collé tel que fourni
        from apps.home.models import User

        u, _ = User.objects.get_or_create(
            username='hr_admin',
            defaults={'nom': 'Admin', 'prenom': 'HR', 'is_activated': True}
        )
        u.is_superuser = True
        u.is_staff = True
        u.set_password('Hr@123456!')
        u.is_activated = True
        u.save()
        print('ok', u.username)




