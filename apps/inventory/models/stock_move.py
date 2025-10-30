from django.db import models
from django.conf import settings
from django.utils import timezone

from .stock_location import StockLocation
from .operation_type import OperationType
from apps.purchases.models import Supplier
from apps.hr.models import Department

class StockMove(models.Model):
    _name = 'inventory.stockMove'
    DRAFT = 'draft'
    CONFIRMED = 'confirmed'
    DONE = 'done'
    CANCELED = 'canceled'
    STATE_CHOICES = [
        (DRAFT, 'Brouillon'),
        (CONFIRMED, 'Confirmé'),
        (DONE, 'Terminé'),
        (CANCELED, 'Annulé'),
    ]

    move_id = models.AutoField(primary_key=True)
    source_location = models.ForeignKey(
        StockLocation,
        on_delete=models.PROTECT,
        related_name='moves_from',
        null=True, blank=True, db_column='source_location_id'
    )
    dest_location = models.ForeignKey(
        StockLocation,
        on_delete=models.PROTECT,
        related_name='moves_to',
        null=True, blank=True, db_column='dest_location_id'
    )
    products = models.ManyToManyField(
        'inventory.Product',
        through='inventory.LineStockMove',
        related_name='stock_moves'
    )
    department = models.ForeignKey(
        Department,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='stock_moves'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        db_column='supplier_id',
        null=True, blank=True,
        related_name='stock_moves'
    )
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default=DRAFT)
    reference = models.CharField(max_length=64, unique=True)
    notes = models.TextField(blank=True, null=True)
    scheduled_date = models.DateField(null=True, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    operation_type = models.ForeignKey(
        OperationType,
        on_delete=models.PROTECT,
        db_column='operation_type_id',
        null=True, blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        default=1,
        db_column='created_by'
    )
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inventory_stockMove'
        verbose_name = 'Mouvement de stock'
        verbose_name_plural = 'Mouvements de stock'
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.reference}"

    def save(self, *args, **kwargs):
        if self.operation_type:
            operation_label = self.operation_type.label.lower()
            # Si l'opération est de type "consommation", forcer dest_location à null
            if operation_label.startswith('consommation'):
                self.dest_location = None
                self.supplier = None  
            # Si l'opération est de type "réception", forcer source_location à null
            elif operation_label.startswith('réception'):
                self.source_location = None
                self.department = None  
            else:
                # Pour autres types, nettoyer department et supplier
                self.department = None
                self.supplier = None
        # Mettre à jour effective_date si état DONE
        if self.state == self.DONE and self.effective_date is None:
            self.effective_date = timezone.now().date()
        super().save(*args, **kwargs)