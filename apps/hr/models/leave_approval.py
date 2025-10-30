from django.db import models
from .employee import Employee

class LeaveApproval(models.Model):
    DECISION_CHOICES = [
        ('approved', 'Approuvé'),
        ('refused', 'Refusé'),
    ]
    
    approval_id = models.AutoField(primary_key=True)
    request = models.OneToOneField(
        'LeaveRequest',
        on_delete=models.CASCADE,
        related_name='approval',
        verbose_name="Demande de congé"
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_approvals',
        verbose_name="Approbateur",
        null=True,
        blank=True
    )
    decision = models.CharField(
        max_length=10,
        choices=DECISION_CHOICES,
        verbose_name="Décision"
    )
    decision_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de décision"
    )
    comments = models.TextField(
        null=True,
        blank=True,
        verbose_name="Commentaires"
    )
    
    class Meta:
        verbose_name = "Approbation de congé"
        verbose_name_plural = "Approbations de congés"
        db_table = 'hr_leave_approval'
        ordering = ['-decision_date']
    
    def __str__(self):
        return f"Approbation pour {self.request} - {self.get_decision_display()}"
    
    def save(self, *args, **kwargs):
        # Mettre à jour le statut de la demande en fonction de la décision
        super().save(*args, **kwargs)
        
        # Mettre à jour le statut de la demande
        if self.decision == 'approved':
            self.request.status = 'approved'
        elif self.decision == 'refused':
            self.request.status = 'refused'
        
        # Enregistrer la demande avec le nouveau statut
        self.request.save(update_fields=['status']) 