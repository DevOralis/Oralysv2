#!/usr/bin/env python
"""
Script de vérification rapide pour le module therapeutic_activities
"""

import os
import sys
import django

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.apps import apps

def check_database():
    """Vérifier la connexion à la base de données"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✓ Connexion à la base de données : OK")
        return True
    except Exception as e:
        print(f"✗ Erreur de connexion à la base de données : {e}")
        return False

def check_migrations():
    """Vérifier les migrations"""
    try:
        from django.core.management import call_command
        from io import StringIO
        
        out = StringIO()
        call_command('showmigrations', 'therapeutic_activities', stdout=out)
        migrations = out.getvalue()
        
        if 'therapeutic_activities' in migrations:
            print("✓ Migrations therapeutic_activities : OK")
            return True
        else:
            print("✗ Migrations therapeutic_activities : MANQUANTES")
            return False
    except Exception as e:
        print(f"✗ Erreur lors de la vérification des migrations : {e}")
        return False

def check_models():
    """Vérifier que les modèles sont bien enregistrés"""
    try:
        app_config = apps.get_app_config('therapeutic_activities')
        models = app_config.get_models()
        
        expected_models = [
            'ActivityType', 'ActivityLocation', 'Activity', 
            'Session', 'Participation', 'ErgotherapyEvaluation',
            'CoachingSession', 'SocialReport'
        ]
        
        model_names = [model.__name__ for model in models]
        
        for expected in expected_models:
            if expected in model_names:
                print(f"✓ Modèle {expected} : OK")
            else:
                print(f"✗ Modèle {expected} : MANQUANT")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Erreur lors de la vérification des modèles : {e}")
        return False

def check_urls():
    """Vérifier que les URLs sont bien configurées"""
    try:
        from django.urls import reverse, NoReverseMatch
        
        test_urls = [
            'therapeutic_activities:activities_home',
            'therapeutic_activities:configuration',
            'therapeutic_activities:activity_list',
            'therapeutic_activities:session_list',
            'therapeutic_activities:participation_list',
        ]
        
        for url_name in test_urls:
            try:
                reverse(url_name)
                print(f"✓ URL {url_name} : OK")
            except NoReverseMatch:
                print(f"✗ URL {url_name} : MANQUANTE")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Erreur lors de la vérification des URLs : {e}")
        return False

def check_admin():
    """Vérifier que l'admin est configuré"""
    try:
        from django.contrib import admin
        from apps.therapeutic_activities.models import (
            ActivityType, ActivityLocation, Activity, Session, 
            Participation, ErgotherapyEvaluation, CoachingSession, SocialReport
        )
        
        registered_models = [model.__name__ for model in admin.site._registry.keys()]
        
        expected_admin_models = [
            'ActivityType', 'ActivityLocation', 'Activity', 
            'Session', 'Participation', 'ErgotherapyEvaluation',
            'CoachingSession', 'SocialReport'
        ]
        
        for expected in expected_admin_models:
            if expected in registered_models:
                print(f"✓ Admin {expected} : OK")
            else:
                print(f"✗ Admin {expected} : MANQUANT")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Erreur lors de la vérification de l'admin : {e}")
        return False

def main():
    """Fonction principale de vérification"""
    print("🔍 Vérification du module therapeutic_activities...")
    print("=" * 50)
    
    checks = [
        ("Base de données", check_database),
        ("Migrations", check_migrations),
        ("Modèles", check_models),
        ("URLs", check_urls),
        ("Admin", check_admin),
    ]
    
    all_ok = True
    
    for name, check_func in checks:
        print(f"\n📋 Vérification : {name}")
        print("-" * 30)
        if not check_func():
            all_ok = False
    
    print("\n" + "=" * 50)
    if all_ok:
        print("🎉 Toutes les vérifications sont OK !")
        print("\n📝 Prochaines étapes :")
        print("1. Créer les données de test : python manage.py create_test_data")
        print("2. Lancer le serveur : python manage.py runserver")
        print("3. Tester l'URL : http://localhost:8000/therapeutic_activities/activities_home/")
    else:
        print("❌ Certaines vérifications ont échoué.")
        print("\n🔧 Actions à effectuer :")
        print("1. Vérifier la configuration de la base de données")
        print("2. Exécuter : python manage.py makemigrations therapeutic_activities")
        print("3. Exécuter : python manage.py migrate")
        print("4. Relancer ce script de vérification")

if __name__ == '__main__':
    main() 