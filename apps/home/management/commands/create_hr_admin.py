from django.core.management.base import BaseCommand
from apps.home.models import User


class Command(BaseCommand):
    help = "Create or update a superuser with full HR access"

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True, help='Username to create/update')
        parser.add_argument('--password', required=True, help='Plain password to set')
        parser.add_argument('--first_name', default='HR', help='User first name')
        parser.add_argument('--last_name', default='Admin', help='User last name')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        prenom = options['first_name']
        nom = options['last_name']

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'prenom': prenom,
                'nom': nom,
                'is_activated': True,
            }
        )

        # Ensure flags and password
        user.is_superuser = True
        user.is_staff = True
        user.is_activated = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created HR superuser '{username}'"))
        else:
            self.stdout.write(self.style.WARNING(f"Updated existing user '{username}' to HR superuser"))

        self.stdout.write(self.style.SUCCESS("Username: ") + username)
        self.stdout.write(self.style.SUCCESS("Password: ") + password)



