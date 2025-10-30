from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from apps.hr.models.employee import Employee
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth import get_user_model
class UserManager(BaseUserManager):
    def create_user(self, username, nom, prenom, password=None, is_activated=False, employee=None):
        if not username:
            raise ValueError('The username field must be set')
        user = self.model(
            username=username,
            nom=nom,
            prenom=prenom,
            is_activated=is_activated,
            employee=employee,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, nom, prenom, password=None):
        user = self.create_user(
            username=username,
            nom=nom,
            prenom=prenom,
            password=password,
            is_activated=True,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)  # Stores hashed password
    is_activated = models.BooleanField(default=False)  # Tracks user activation status
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user'
    )
    is_staff = models.BooleanField(default=False)  # Required for admin access
    is_superuser = models.BooleanField(default=False)  # Required for superuser
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['nom', 'prenom']

    def set_password(self, raw_password):
        """Hash and set the user's password."""
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """Check if the provided password matches the stored hash."""
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.username})"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = 'authz_user'  # Specifies the table name in the database

class UserPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permissions')
    app_name = models.CharField(max_length=50)
    can_read = models.BooleanField(default=False)
    can_write = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'app_name')
        db_table = 'authz_user_permission'  # Specifies the table name in the database
        
        


class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('creation', 'Création'),
        ('modification', 'Modification'),
        ('suppression', 'Suppression'),
        ('impression', 'Impression PDF'),
    )

    id = models.CharField(max_length=20, primary_key=True, editable=False)
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    entity_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object = GenericForeignKey('content_type', 'object_id')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    date_time = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.id:
            # Générer un ID au format OP-XXXXXX
            last_log = AuditLog.objects.order_by('-id').first()
            if last_log and last_log.id.startswith('OP-'):
                try:
                    last_number = int(last_log.id.split('-')[-1])
                    new_number = last_number + 1
                except ValueError:
                    new_number = 1
            else:
                new_number = 1
            self.id = f'OP-{new_number:06d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.action} sur {self.entity_name} ({self.object_id}) par {self.created_by} le {self.date_time}"

    class Meta:
        verbose_name = "Journal d'audit"
        verbose_name_plural = "Journaux d'audit"
        db_table = 'audit_log'