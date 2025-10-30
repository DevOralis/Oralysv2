from django.db import models
from apps.patient.models import Patient
from .room import Room
from .bed import Bed

class Reservation(models.Model):
    RESERVATION_STATUS = (
        ('confirmed', 'Confirmé'),
        ('cancelled', 'Annulé'),
        ('pending', 'En attente'),
    )

    reservation_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='reservations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reservations')
    bed = models.ForeignKey(Bed, on_delete=models.CASCADE, null=True, blank=True, related_name='reservations')
    start_date = models.DateField()
    end_date = models.DateField()
    reservation_status = models.CharField(max_length=20, choices=RESERVATION_STATUS, default='pending')

    class Meta:
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"

    def __str__(self):
        return f"Réservation {self.reservation_id} - {self.patient} ({self.start_date})"