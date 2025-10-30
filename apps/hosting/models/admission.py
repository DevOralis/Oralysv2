from django.db import models
from decimal import Decimal
from apps.patient.models import Patient, Consultation
from .room import Room
from .bed import Bed

class Admission(models.Model):
    ASSIGNMENT_MODE = (
        ('bed', 'Lit'),
        ('room', 'Chambre entière'),
    )

    DISCHARGE_REASON = (
        ('end_of_stay', 'Fin de séjour'),
        ('transfer', 'Transfert'),
        ('death', 'Décès'),
    )

    admission_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='admissions')
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='admissions')
    admission_date = models.DateField()
    assignment_mode = models.CharField(max_length=20, choices=ASSIGNMENT_MODE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='admissions')
    bed = models.ForeignKey(Bed, on_delete=models.CASCADE, null=True, blank=True, related_name='admissions')
    room_type = models.CharField(max_length=50)
    discharge_date = models.DateField(null=True, blank=True)
    discharge_reason = models.CharField(max_length=20, choices=DISCHARGE_REASON, null=True, blank=True)
    notes = models.TextField(blank=True)
    is_invoiced = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Admission"
        verbose_name_plural = "Admissions"

    def __str__(self):
        return f"Admission {self.admission_id} - {self.patient} ({self.admission_date})"
    
    def calculate_stay_duration(self):
        """Calculer la durée du séjour en jours"""
        if self.discharge_date:
            duration = (self.discharge_date - self.admission_date).days
            return max(1, duration)  # Au minimum 1 jour
        else:
            # Si pas de date de sortie, calculer depuis la date d'admission jusqu'à aujourd'hui
            from django.utils import timezone
            today = timezone.now().date()
            duration = (today - self.admission_date).days
            return max(1, duration)
    
    def calculate_room_cost(self):
        """Calculer le coût de la chambre en utilisant les Actes HR (même logique que hosting views)"""
        try:
            from apps.patient.models.acte import Acte
            
            # Mapping des types de chambres vers les actes - mapping étendu
            room_type_mapping = {
                'vip': 'VIP',
                'single': 'Simple',
                'simple': 'Simple', 
                'double': 'Double',
                'chambre simple': 'Simple',
                'chambre double': 'Double',
                'chambre vip': 'VIP'
            }
            
            # Déterminer le type d'acte à chercher
            acte_name = 'Simple'  # par défaut
            
            if hasattr(self.room, 'room_type') and hasattr(self.room.room_type, 'name'):
                room_type_name = self.room.room_type.name.lower()
                acte_name = room_type_mapping.get(room_type_name, 'Simple')
            elif self.room_type:
                # Fallback sur le champ room_type string
                room_type_str = self.room_type.lower()
                acte_name = room_type_mapping.get(room_type_str, 'Simple')
            
            # Récupérer le prix depuis les Actes HR
            try:
                # Essayer d'abord la recherche exacte puis avec icontains
                acte_hebergement = None
                try:
                    acte_hebergement = Acte.objects.get(libelle=acte_name)
                except Acte.DoesNotExist:
                    acte_hebergement = Acte.objects.get(libelle__icontains=acte_name)
                
                price_per_night = acte_hebergement.price
                duration = self.calculate_stay_duration()
                return price_per_night * duration
                
            except Acte.DoesNotExist:
                # Si aucun acte trouvé, utiliser prix par défaut basé sur le type
                default_prices = {
                    'VIP': Decimal('300.00'),
                    'Simple': Decimal('150.00'),
                    'Double': Decimal('200.00')
                }
                default_price = default_prices.get(acte_name, Decimal('150.00'))
                duration = self.calculate_stay_duration()
                return default_price * duration
                
        except (AttributeError, ValueError, ImportError):
            # En cas d'erreur, prix par défaut simple
            duration = self.calculate_stay_duration()
            return Decimal('150.00') * duration
    
    def calculate_companion_cost(self):
        """Calculer le coût de l'accompagnant en utilisant les Actes HR (même logique que hosting views)"""
        try:
            from apps.patient.models.acte import Acte
            from .companion import Companion
            
            # Vérifier s'il y a un accompagnant pour ce patient
            companions = Companion.objects.filter(patient=self.patient)
            
            if companions.exists():
                total_companion_cost = Decimal('0.00')
                
                for companion in companions:
                    if companion.accommodation_start_date and companion.accommodation_end_date:
                        # Calculer nombre de jours d'accompagnement
                        nb_jours_acc = (companion.accommodation_end_date - companion.accommodation_start_date).days
                        if nb_jours_acc <= 0:
                            nb_jours_acc = 1
                        
                        try:
                            acte_accompagnant = Acte.objects.get(libelle__icontains='Accompagnant')
                            companion_cost = acte_accompagnant.price * nb_jours_acc
                            total_companion_cost += companion_cost
                        except Acte.DoesNotExist:
                            # Prix par défaut si acte accompagnant non trouvé
                            default_price = Decimal('50.00')
                            companion_cost = default_price * nb_jours_acc
                            total_companion_cost += companion_cost
                
                return total_companion_cost
            
            return Decimal('0.00')
        except (AttributeError, ValueError, ImportError):
            return Decimal('0.00')
    
    def calculate_room_unit_price(self):
        """Calculer le prix unitaire par jour pour la chambre"""
        try:
            from apps.patient.models.acte import Acte
            
            # Mapping des types de chambres vers les actes - mapping étendu
            room_type_mapping = {
                'vip': 'VIP',
                'single': 'Simple',
                'simple': 'Simple', 
                'double': 'Double',
                'chambre simple': 'Simple',
                'chambre double': 'Double',
                'chambre vip': 'VIP'
            }
            
            # Déterminer le type d'acte à chercher
            acte_name = 'Simple'  # par défaut
            
            if hasattr(self.room, 'room_type') and hasattr(self.room.room_type, 'name'):
                room_type_name = self.room.room_type.name.lower()
                acte_name = room_type_mapping.get(room_type_name, 'Simple')
            elif self.room_type:
                # Fallback sur le champ room_type string
                room_type_str = self.room_type.lower()
                acte_name = room_type_mapping.get(room_type_str, 'Simple')
            
            # Récupérer le prix unitaire depuis les Actes HR
            try:
                # Essayer d'abord la recherche exacte puis avec icontains
                acte_hebergement = None
                try:
                    acte_hebergement = Acte.objects.get(libelle=acte_name)
                except Acte.DoesNotExist:
                    acte_hebergement = Acte.objects.get(libelle__icontains=acte_name)
                
                return acte_hebergement.price  # Prix par jour
                
            except Acte.DoesNotExist:
                # Si aucun acte trouvé, utiliser prix par défaut basé sur le type
                default_prices = {
                    'VIP': Decimal('300.00'),
                    'Simple': Decimal('150.00'),
                    'Double': Decimal('200.00')
                }
                return default_prices.get(acte_name, Decimal('150.00'))
                
        except (AttributeError, ValueError, ImportError):
            # En cas d'erreur, prix par défaut selon le type de chambre
            default_prices = {
                'VIP': Decimal('300.00'),
                'Simple': Decimal('150.00'), 
                'Double': Decimal('200.00'),
                'Chambre Simple': Decimal('150.00'),
                'Chambre Double': Decimal('200.00'),
                'Chambre VIP': Decimal('300.00')
            }
            
            room_type_key = self.room_type if self.room_type else 'Simple'
            return default_prices.get(room_type_key, Decimal('150.00'))
    
    def calculate_companion_unit_price(self):
        """Calculer le prix unitaire par jour pour l'accompagnant"""
        companion_cost = self.calculate_companion_cost()
        duration = self.calculate_stay_duration()
        if companion_cost > 0 and duration > 0:
            return companion_cost / duration
        return Decimal('0.00')

    def calculate_total_cost(self):
        """Calculer le coût total de l'admission (chambre + accompagnant)"""
        room_cost = self.calculate_room_cost()
        companion_cost = self.calculate_companion_cost()
        return room_cost + companion_cost
