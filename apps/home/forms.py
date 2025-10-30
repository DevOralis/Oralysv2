import logging
from django import forms
from django.db import transaction
from apps.home.models import User, UserPermission
from apps.hr.models.employee import Employee

# Set up logging
logger = logging.getLogger(__name__)

from django.apps import apps as django_apps

class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Mot de passe",
        required=False
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirmer le mot de passe",
        required=False
    )

    class Meta:
        model = User
        fields = ['nom', 'prenom', 'username', 'password', 'password_confirm', 'is_activated', 'employee']
        labels = {
            'nom': 'Nom',
            'prenom': 'Prénom',
            'username': "Nom d'utilisateur",
            'is_activated': 'Activé',
            'employee': 'Employé associé',
        }
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'is_activated': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'employee': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically get installed apps
        self.apps = [
            {'name': app_config.name, 'label': app_config.verbose_name or app_config.name.split('.')[-1].capitalize()}
            for app_config in django_apps.get_app_configs()
            if app_config.name.startswith('apps.')  # Filter only your custom apps
        ]

    def clean(self):
        cleaned_data = super().clean()
        
        # Validate required fields
        nom = cleaned_data.get('nom')
        prenom = cleaned_data.get('prenom')
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if not nom:
            self.add_error('nom', "Le nom est requis.")
        if not prenom:
            self.add_error('prenom', "Le prénom est requis.")
        if not username:
            self.add_error('username', "Le nom d'utilisateur est requis.")

        # Validate password only for new users
        if not self.instance.pk:  # New user
            if not password:
                self.add_error('password', "Le mot de passe est requis pour un nouvel utilisateur.")
            if password and password != password_confirm:
                self.add_error('password_confirm', "Les mots de passe ne correspondent pas.")

        # Validate username uniqueness
        if username:
            queryset = User.objects.filter(username=username)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                self.add_error('username', "Ce nom d'utilisateur est déjà pris.")

        # Validate permissions for all apps
        cleaned_data['permissions'] = {}
        for app in self.apps:
            app_name = app['name'].split('.')[-1]  # Extract the app name (e.g., 'pharmacy' from 'apps.pharmacy')
            cleaned_data['permissions'][app_name] = {
                'read': self.data.get(f'permissions[{app_name}][read]') == 'on',
                'write': self.data.get(f'permissions[{app_name}][write]') == 'on',
                'update': self.data.get(f'permissions[{app_name}][update]') == 'on',
                'delete': self.data.get(f'permissions[{app_name}][delete]') == 'on',
            }
        
        return cleaned_data

    def save(self, commit=True):
        try:
            with transaction.atomic():
                user = super().save(commit=False)
                password = self.cleaned_data.get('password')

                # Si c'est une mise à jour (self.instance.pk existe) et que le mot de passe est vide,
                # on ne touche pas au mot de passe existant.
                # Si un nouveau mot de passe est fourni, on le met à jour.
                if password:
                    user.set_password(password)
                # Si c'est une mise à jour et qu'aucun mot de passe n'est fourni,
                # on préserve l'ancien mot de passe en le rechargeant depuis la BDD.
                elif self.instance.pk:
                    user.password = User.objects.get(pk=self.instance.pk).password
                if commit:
                    user.save()
                    self.save_m2m()
                    # Save permissions for all apps
                    permissions = self.cleaned_data.get('permissions', {})
                    for app_name, perms in permissions.items():
                        UserPermission.objects.update_or_create(
                            user=user,
                            app_name=app_name,
                            defaults={
                                'can_read': perms['read'],
                                'can_write': perms['write'],
                                'can_update': perms['update'],
                                'can_delete': perms['delete'],
                            }
                        )
                return user
        except Exception as e:
            logger.error(f"Error saving user: {str(e)}")
            raise