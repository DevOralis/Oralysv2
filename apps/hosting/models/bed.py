from django.db import models
from .room import Room
from .bed_status import BedStatus

class Bed(models.Model):
    bed_id = models.CharField(max_length=50, primary_key=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='beds')
    bed_number = models.CharField(max_length=50)
    bed_status = models.ForeignKey(BedStatus, on_delete=models.PROTECT, related_name='beds')

    class Meta:
        verbose_name = "Lit"
        verbose_name_plural = "Lits"

    def __str__(self):
        return f"Lit {self.bed_number} - {self.room.room_name}"