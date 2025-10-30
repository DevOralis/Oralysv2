from .models import Incident, Intervention

def incident_notification(request):
    nb_incidents_ouverts = Incident.objects.filter(statut__in=['nouveau', 'en_cours']).count()
    return {'nb_incidents_ouverts': nb_incidents_ouverts}

def intervention_notification(request):
    nb_interventions_ouvertes = Intervention.objects.filter(statut__in=['planifiee', 'en_cours']).count()
    return {'nb_interventions_ouvertes': nb_interventions_ouvertes}