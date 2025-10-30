from django.db import models
from .room_type import RoomType

class Room(models.Model):
    ROOM_TYPE = (
        ('single', 'Single'),
        ('double', 'Double'),
        ('vip', 'VIP'),
    )
    STATUS = (
        ('available', 'Disponible'),
        ('occupied', 'Occupée'),
        ('maintenance', 'En maintenance'),
    )

    room_id = models.CharField(max_length=50, primary_key=True)
    room_name = models.CharField(max_length=100, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.PROTECT, related_name='rooms')
    capacity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS, default='available')
    description = models.TextField(blank=True, null=True)  # Add if needed

    class Meta:
        verbose_name = "Room"
        verbose_name_plural = "Rooms"

    def __str__(self):
        return f"{self.room_name} ({self.room_type})"