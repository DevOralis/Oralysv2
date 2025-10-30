from django.db import models
from django.conf import settings
from django.utils import timezone

from .stock_location import PharmacyStockLocation
from .pharmacy_operation_type import PharmacyOperationType
from .supplier import PharmacySupplier
from apps.hr.models import Department
from .pharmacy_order import PharmacyOrder

class PharmacyStockMove(models.Model):
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
        PharmacyStockLocation, on_delete=models.PROTECT, related_name='pharmacy_moves_from', null=True, blank=True
    )
    dest_location = models.ForeignKey(
        PharmacyStockLocation, on_delete=models.PROTECT, related_name='pharmacy_moves_to', null=True, blank=True
    )
    products = models.ManyToManyField(
        'PharmacyProduct',
        through='PharmacyLineStockMove',
        related_name='pharmacy_stock_moves'
    )
    department = models.ForeignKey(
        Department, null=True, blank=True, on_delete=models.SET_NULL, related_name='pharmacy_stock_moves'
    )
    supplier = models.ForeignKey(
        PharmacySupplier, on_delete=models.PROTECT, null=True, blank=True, related_name='pharmacy_stock_moves'
    )
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default=DRAFT)
    reference = models.CharField(max_length=64, unique=True)
    notes = models.TextField(blank=True, null=True)
    scheduled_date = models.DateField(null=True, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    operation_type = models.ForeignKey(
        PharmacyOperationType, on_delete=models.PROTECT, null=True, blank=True
    )
    # order = models.ForeignKey(
    #     PharmacyOrder,
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name='pharmacy_stock_moves'
    # )  # Commenté temporairement car la colonne order_id n'existe pas en base
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, default=1
    )
    date_created = models.DateTimeField(auto_now_add=True)


    class Meta:
        db_table = 'pharmacy_stock_move'
        verbose_name = 'Mouvement de stock pharmacie'
        verbose_name_plural = 'Mouvements de stock pharmacie'
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.reference}"

    # -- Compatibility helpers: some views expect an optional 'order' relation --
    @property
    def order(self):
        """Return None when the optional PharmacyOrder relation is not present."""
        return None

    @order.setter
    def order(self, value):
        """Silently ignore assignment when relation does not exist in DB schema."""
        # No-op; prevents AttributeError when code sets move.order
        pass

    def save(self, *args, **kwargs):
        if self.operation_type:
            operation_label = self.operation_type.label.lower()
            if operation_label.startswith('consommation'):
                self.dest_location = None
                self.supplier = None
            elif operation_label.startswith('réception'):
                self.source_location = None
                self.department = None
            else:
                self.department = None
                self.supplier = None
        if self.state == self.DONE and self.effective_date is None:
            self.effective_date = timezone.now().date()
        super().save(*args, **kwargs)


