from django.urls import path
from . import views
from .views import consultation, complete_consultation, consultation_pdf, appointment, appointment_table

app_name = 'patient'

urlpatterns = [
    path('', views.patient_list_create, name='patient_list_create'),
    path('delete/<int:patient_id>/', views.delete_patient, name='delete_patient'),
    path('delete-medical-document/<int:document_id>/', views.delete_medical_document, name='delete_medical_document'),
    path('pdf/<int:patient_id>/', views.patient_pdf, name='patient_pdf'),
    path('consultation/', consultation, name='consultation'),
    path('consultation/add/', views.add_consultation, name='add_consultation'),
    path('consultation/delete/<int:consultation_id>/', views.delete_consultation, name='delete_consultation'),
    path('appointment/delete/<int:appointment_id>/', views.delete_appointment, name='delete_appointment'),
    path('admission/', views.admission_list, name='admission_list'),
    path('admission/delete/<int:consultation_id>/', views.delete_admission, name='delete_admission'),
    path('appointments/', appointment, name='appointment'),
    path('appointments/table/', appointment_table, name='appointment_table'),
    path('appointments/<int:rdv_id>/complete/', complete_consultation, name='complete_consultation'),
    path('api/medecin-appointments/', views.medecin_appointments_json, name='medecin_appointments_json'),
    path('insurance-records/', views.insurance_records, name='insurance_records'),
    path('mutuelle-edit-form/<int:patient_id>/', views.mutuelle_edit_form, name='mutuelle_edit_form'),
    path('consultation-pdf/<int:consultation_id>/', consultation_pdf, name='consultation_pdf'),
    path('ajax/consultation/<int:consultation_id>/', views.get_consultation_details, name='ajax_consultation_details'),
    path('ajax/appointment/<int:appointment_id>/', views.get_appointment_details, name='ajax_appointment_details'),
    path('statistics/', views.patient_statistics, name='patient_statistics'),
    
    # URLs pour facturation
    path('billing-management/', views.billing_management, name='billing_management'),
    path('patient-summary/', views.patient_summary, name='patient_summary'),
    path('simple-invoice-form/', views.simple_invoice_form, name='simple_invoice_form'),
    path('patient/<int:patient_id>/invoice-pdf/', views.generate_patient_invoice_pdf, name='generate_patient_invoice_pdf'),
    path('facturation/invoice/<int:invoice_id>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    path('billing/<int:bill_id>/mark-paid/', views.mark_bill_as_paid, name='mark_bill_as_paid'),
    path('billing/<int:bill_id>/process-payment/', views.process_payment, name='process_payment'),
    path('payment-details/<int:payment_id>/', views.payment_details_json, name='payment_details_json'),
    path('payment-receipt/<int:payment_id>/pdf/', views.payment_receipt_pdf, name='payment_receipt_pdf'),
    path('payments/', views.payments_list, name='payments_list'),
    
    # URLs pour gestion des actes
    path('actes/', views.acte_list, name='acte_list'),
    
    # URL pour les paramètres / configuration
    path('settings/', views.patient_settings, name='patient_settings'),
]
