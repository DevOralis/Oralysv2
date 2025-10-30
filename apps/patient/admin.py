from django.contrib import admin
from .models import (
    Patient, Consultation, Invoice, Appointment, MedicalDocument, 
    EmergencyContact, Acte, Payment, PartialPayment,
    ActeTherapeutique, DocumentType, PatientSource
)

# Register your models here.

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_identifier', 'last_name', 'first_name', 'gender', 'birth_date', 'phone')
    search_fields = ('last_name', 'first_name', 'patient_identifier', 'cin', 'phone')
    list_filter = ('gender', 'has_insurance')

@admin.register(MedicalDocument)
class MedicalDocumentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'document_type', 'file_name', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('patient__last_name', 'patient__first_name', 'description')
    date_hierarchy = 'uploaded_at'
    
    def file_name(self, obj):
        return obj.file_name
    file_name.short_description = 'Nom du fichier'

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'medecin', 'date', 'hospitalisation')
    list_filter = ('hospitalisation', 'date')
    search_fields = ('patient__last_name', 'patient__first_name', 'medecin__full_name')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'medecin', 'date_heure', 'statut', 'mode')
    list_filter = ('statut', 'mode', 'date_heure')
    search_fields = ('patient__last_name', 'patient__first_name', 'nom', 'prenom')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'patient', 'total_amount', 'status', 'invoice_date')
    list_filter = ('status', 'invoice_date')
    search_fields = ('invoice_number', 'patient__last_name', 'patient__first_name')

@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'relationship')
    search_fields = ('name', 'phone')

@admin.register(Acte)
class ActeAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'price')
    search_fields = ('libelle',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('journal', 'amount', 'payment_date', 'payment_mode')
    list_filter = ('payment_mode', 'payment_date')
    search_fields = ('journal', 'memo')

@admin.register(PartialPayment)
class PartialPaymentAdmin(admin.ModelAdmin):
    list_display = ('payment', 'payment_number', 'payment_channel', 'amount', 'payment_date', 'due_date')
    list_filter = ('payment_channel', 'payment_date', 'due_date')
    search_fields = ('payment__memo', 'payment__billing_history__invoice_number')
    date_hierarchy = 'payment_date'

@admin.register(ActeTherapeutique)
class ActeTherapeutiqueAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'price', 'duration', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('libelle', 'description')
    ordering = ('libelle',)

@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    ordering = ('name',)

@admin.register(PatientSource)
class PatientSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'color', 'icon', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    ordering = ('name',)