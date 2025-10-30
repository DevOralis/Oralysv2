from django.db import models
from .social_contribution import SocialContribution
from .prime import Prime
from datetime import date
import unicodedata

class ModelCalcul(models.Model):
    libelle = models.CharField(max_length=255)
    social_contributions = models.ManyToManyField(SocialContribution, blank=True)
    primes = models.ManyToManyField(Prime, blank=True)

    def __str__(self):
        return self.libelle 

def normalize_label(label):
    # Supprime les accents, met en minuscules, enlève les espaces
    label = label.lower().strip()
    label = ''.join(c for c in unicodedata.normalize('NFD', label) if unicodedata.category(c) != 'Mn')
    label = label.replace("'", "").replace('’', '').replace(' ', '')
    return label

def cnss_prime(salaire_base):
    """Calcule la cotisation CNSS: Min(salaire_base, 6000) * 3.96%"""
    salaire_base = float(salaire_base)
    return min(salaire_base, 6000) * 0.0396

def amo_prime(salaire_base):
    """Calcule la cotisation AMO: salaire_base * 2.26%"""
    salaire_base = float(salaire_base)
    return salaire_base * 0.0226

def cimr_prime(salaire_base):
    """Calcule la cotisation CIMR: salaire_base * 3%"""
    salaire_base = float(salaire_base)
    return salaire_base * 0.03

def frais_professionnels(salaire_base, cnss, amo, cimr):
    """Calcule les frais professionnels: Min(salaire_base - (cnss+amo+cimr), 500) * 20%"""
    salaire_base = float(salaire_base)
    base = salaire_base - (cnss + amo + cimr)
    return min(base, 500) * 0.2 

def prime_transport(salaire_base):
    """Prime de transport: +300 DH"""
    salaire_base = float(salaire_base)
    return 300

def prime_repas(salaire_base):
    """Prime de repas: +300 DH"""
    salaire_base = float(salaire_base)
    return 300

def prime_logement(salaire_base):
    """Prime de logement: +500 DH"""
    salaire_base = float(salaire_base)
    return 500

def prime_anciennete(salaire_base, date_debut_contrat):
    """Prime d'ancienneté selon l'ancienneté en années."""
    salaire_base = float(salaire_base)
    if not date_debut_contrat:
        return 0
    today = date.today()
    years = today.year - date_debut_contrat.year - ((today.month, today.day) < (date_debut_contrat.month, date_debut_contrat.day))
    if years >= 20:
        return salaire_base * 0.25
    elif years >= 15:
        return salaire_base * 0.20
    elif years >= 10:
        return salaire_base * 0.15
    elif years >= 2:
        return salaire_base * 0.10
    elif years >= 2:
        return salaire_base * 0.05
    else:
        return 0 

def get_total_primes_et_cotisations(employee):
    """
    Calcule dynamiquement toutes les primes et cotisations pour un employé selon son ModelCalcul.
    Seuls les éléments cochés (liés au modèle) sont pris en compte.
    Retourne un dictionnaire détaillé.
    """
    salaire_base = employee.base_salary
    model = employee.model_calcul
    date_debut_contrat = None
    if hasattr(employee, 'contract') and employee.contract:
        date_debut_contrat = employee.contract.start_date

    # Primes
    primes = {}
    for prime in model.primes.all():
        libelle = normalize_label(prime.libelle if hasattr(prime, 'libelle') else prime.label)
        if 'transport' in libelle:
            primes['prime_transport'] = prime_transport(salaire_base)
        elif 'repas' in libelle:
            primes['prime_repas'] = prime_repas(salaire_base)
        elif 'logement' in libelle:
            primes['prime_logement'] = prime_logement(salaire_base)
        # Ajoute ici d'autres types de primes si besoin
    # Debug : afficher toutes les primes du modèle de calcul
    print('[DEBUG] Primes du modèle de calcul:', [p.libelle if hasattr(p, 'libelle') else p.label for p in model.primes.all()])
    # Prime d'ancienneté (toujours calculée si présente dans le modèle)
    # On prend la date de début de contrat de l'employé
    date_debut_contrat = None
    if hasattr(employee, 'contract') and employee.contract and employee.contract.start_date:
        date_debut_contrat = employee.contract.start_date
    prime_anciennete_detectee = any(
        any(variant in normalize_label(p.libelle if hasattr(p, 'libelle') else p.label)
            for variant in ['anciennete', 'anciennet', 'aciennete'])
        for p in model.primes.all()
    )
    if prime_anciennete_detectee:
        prime_val = prime_anciennete(salaire_base, date_debut_contrat)
        from datetime import date
        if date_debut_contrat:
            today = date.today()
            years = today.year - date_debut_contrat.year - ((today.month, today.day) < (date_debut_contrat.month, date_debut_contrat.day))
            print(f"[DEBUG] Prime ancienneté: {prime_val} (ancienneté: {years} ans, début: {date_debut_contrat})")
        else:
            print(f"[DEBUG] Prime ancienneté: {prime_val} (date de début de contrat introuvable)")
        primes['prime_anciennete'] = prime_val
    else:
        print(f"[DEBUG] Prime ancienneté: non cochée dans le modèle de calcul")
    print('Primes détectées et montants:', primes)

    total_primes = sum(primes.values())

    # Cotisations sociales
    cotisations = {}
    for cot in model.social_contributions.all():
        lib = normalize_label(cot.label)
        if 'cnss' in lib:
            cotisations['cnss'] = cnss_prime(salaire_base)
        elif 'amo' in lib:
            cotisations['amo'] = amo_prime(salaire_base)
        elif 'cimr' in lib:
            cotisations['cimr'] = cimr_prime(salaire_base)
        # Ajoute ici d'autres cotisations si besoin
    print('Cotisations détectées et montants:', cotisations)
    total_cotisations = sum(cotisations.values())

    # Frais professionnels (calculés si demandé)
    frais = frais_professionnels(salaire_base, cotisations.get('cnss',0), cotisations.get('amo',0), cotisations.get('cimr',0))

    salaire_base_f = float(salaire_base)
    total_primes_f = float(total_primes)
    total_cotisations_f = float(total_cotisations)
    return {
        'salaire_base': salaire_base_f,
        'primes': primes,
        'total_primes': total_primes_f,
        'cotisations': cotisations,
        'total_cotisations': total_cotisations_f,
        'frais_professionnels': frais,
        'salaire_brut': salaire_base_f + total_primes_f,
        'salaire_net': salaire_base_f + total_primes_f - total_cotisations_f,
    } 