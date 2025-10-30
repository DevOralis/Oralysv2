# Module Activités Thérapeutiques

## 🎯 **Objectif**
Module de gestion des activités thérapeutiques pour un établissement de santé, sans gestion d'authentification ni permissions pour le moment.

## 📋 **Fonctionnalités Disponibles**

### **1. Configuration**
- ✅ Gestion des types d'activités
- ✅ Gestion des salles d'activités
- ✅ Interface AJAX pour création/suppression

### **2. Activités**
- ✅ CRUD complet des activités
- ✅ Association avec coach et type d'activité
- ✅ Recherche et filtrage

### **3. Sessions**
- ✅ CRUD complet des sessions
- ✅ Gestion des horaires et capacités
- ✅ Filtrage par date, activité, statut

### **4. Participations**
- ✅ CRUD complet des participations
- ✅ Gestion des statuts (présent, absent, excusé)
- ✅ Création en masse

### **5. Évaluations Spécialisées**
- ✅ Évaluations ergothérapiques
- ✅ Sessions de coaching
- ✅ Rapports sociaux

### **6. Statistiques et Rapports**
- ✅ Tableau de bord statistiques
- ✅ Suivi patient
- ✅ Rapports par type d'activité
- ✅ Système d'alertes

### **7. Calendrier**
- ✅ Vue calendrier des sessions

## 🚀 **Étapes pour Tester le Module**

### **Étape 1 : Vérifier la Configuration**
```bash
# Vérifier que le module est bien installé
python manage.py check therapeutic_activities

# Vérifier les URLs
python manage.py show_urls | grep therapeutic_activities
```

### **Étape 2 : Créer les Migrations**
```bash
# Créer les migrations si elles n'existent pas
python manage.py makemigrations therapeutic_activities

# Appliquer les migrations
python manage.py migrate
```

### **Étape 3 : Créer des Données de Test**
```bash
# Accéder au shell Django
python manage.py shell

# Dans le shell, exécuter :
from apps.hr.models.employee import Employee, Position
from apps.patient.models import Patient
from apps.therapeutic_activities.models import ActivityType, ActivityLocation

# Créer une position coach
coach_position = Position.objects.create(name='Coach')

# Créer un employé coach
coach = Employee.objects.create(
    first_name='John',
    last_name='Doe',
    full_name='John Doe',
    position=coach_position
)

# Créer un patient
patient = Patient.objects.create(
    first_name='Jane',
    last_name='Smith',
    full_name='Jane Smith'
)

# Créer un type d'activité
activity_type = ActivityType.objects.create(
    name='Thérapie physique',
    description='Activités de rééducation physique'
)

# Créer une salle
location = ActivityLocation.objects.create(
    name='Salle de thérapie',
    address='Bâtiment A, 1er étage',
    capacity=10
)

# Quitter le shell
exit()
```

### **Étape 4 : Lancer le Serveur**
```bash
python manage.py runserver
```

### **Étape 5 : Tester les URLs**
Accéder aux URLs suivantes dans votre navigateur :

1. **Page d'accueil** : `http://localhost:8000/therapeutic_activities/activities_home/`
2. **Configuration** : `http://localhost:8000/therapeutic_activities/configuration/`
3. **Liste des activités** : `http://localhost:8000/therapeutic_activities/activities/`
4. **Liste des sessions** : `http://localhost:8000/therapeutic_activities/sessions/`
5. **Liste des participations** : `http://localhost:8000/therapeutic_activities/participations/`
6. **Statistiques** : `http://localhost:8000/therapeutic_activities/statistics/`
7. **Alertes** : `http://localhost:8000/therapeutic_activities/alerts/`
8. **Calendrier** : `http://localhost:8000/therapeutic_activities/sessions/calendar/`

### **Étape 6 : Tester les Fonctionnalités**

#### **A. Créer une Activité**
1. Aller sur `/therapeutic_activities/activities/create/`
2. Remplir le formulaire :
   - Titre : "Séance de kinésithérapie"
   - Description : "Séance de rééducation"
   - Type : Sélectionner "Thérapie physique"
   - Coach : Sélectionner "John Doe"
3. Cliquer sur "Créer"

#### **B. Créer une Session**
1. Aller sur `/therapeutic_activities/sessions/create/`
2. Remplir le formulaire :
   - Activité : Sélectionner l'activité créée
   - Salle : Sélectionner "Salle de thérapie"
   - Date : Aujourd'hui
   - Heure début : 09:00
   - Heure fin : 10:00
   - Participants max : 5
3. Cliquer sur "Créer"

#### **C. Créer une Participation**
1. Aller sur `/therapeutic_activities/participations/create/`
2. Remplir le formulaire :
   - Patient : Sélectionner "Jane Smith"
   - Session : Sélectionner la session créée
   - Statut : "Présent"
3. Cliquer sur "Créer"

#### **D. Tester les Recherches**
1. Aller sur `/therapeutic_activities/activities/`
2. Utiliser la barre de recherche pour chercher "kinésithérapie"
3. Utiliser les filtres par type et coach

#### **E. Tester les Statistiques**
1. Aller sur `/therapeutic_activities/statistics/`
2. Vérifier que les statistiques s'affichent correctement

### **Étape 7 : Lancer les Tests**
```bash
# Lancer tous les tests du module
python manage.py test apps.therapeutic_activities

# Lancer un test spécifique
python manage.py test apps.therapeutic_activities.tests.ModelTests

# Lancer les tests avec plus de détails
python manage.py test apps.therapeutic_activities --verbosity=2
```

## 🔧 **Structure des Fichiers**

```
apps/therapeutic_activities/
├── models.py              # Modèles de données
├── views.py               # Logique des vues (sans auth)
├── forms.py               # Formulaires
├── urls.py                # Configuration des URLs
├── admin.py               # Interface d'administration
├── tests.py               # Tests unitaires
├── templates/             # Templates HTML
├── static/                # Fichiers statiques (CSS/JS)
└── migrations/            # Migrations de base de données
```

## 📊 **Modèles Principaux**

### **ActivityType**
- Types d'activités (Thérapie physique, Ergothérapie, etc.)

### **ActivityLocation**
- Salles d'activités avec capacités

### **Activity**
- Activités avec coach et type

### **Session**
- Sessions programmées avec horaires

### **Participation**
- Participation des patients aux sessions

### **Évaluations Spécialisées**
- ErgotherapyEvaluation
- CoachingSession
- SocialReport

## ⚠️ **Notes Importantes**

1. **Pas d'authentification** : Toutes les vues sont accessibles sans login
2. **Pas de permissions** : Aucune restriction d'accès
3. **Données de test** : Créer les données de base avant de tester
4. **Templates manquants** : Les templates HTML doivent être créés
5. **CSS/JS** : Les fichiers statiques doivent être ajoutés

## 🎨 **Prochaines Étapes pour le Frontend**

1. **Créer les templates HTML** pour toutes les vues
2. **Ajouter les fichiers CSS** pour le style
3. **Ajouter les fichiers JavaScript** pour les interactions AJAX
4. **Créer les icônes et images** nécessaires
5. **Tester l'interface utilisateur** complète

## 🐛 **Dépannage**

### **Erreur "NoReverseMatch"**
- Vérifier que `app_name = 'therapeutic_activities'` est dans `urls.py`
- Vérifier que le namespace est correctement configuré dans `config/urls.py`

### **Erreur "Table doesn't exist"**
- Exécuter `python manage.py migrate`

### **Erreur "Module not found"**
- Vérifier que l'app est dans `INSTALLED_APPS` dans `settings.py`

### **Erreur "Template not found"**
- Créer les templates HTML manquants dans `templates/`

## 📞 **Support**

Pour toute question ou problème, vérifier :
1. Les logs Django dans la console
2. Les erreurs dans le navigateur (F12)
3. La configuration des URLs
4. Les migrations de base de données 