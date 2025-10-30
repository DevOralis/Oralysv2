from .base import *

DEBUG = True

# Autorise les requêtes en local
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
# Configuration des médias
MEDIA_ROOT = BASE_DIR.parent / 'media'  # Dossier media à la racine du projet
MEDIA_URL = '/media/'  # URL pour accéder aux fichiers média
