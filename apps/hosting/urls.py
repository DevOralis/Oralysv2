# urls.py for hosting app
from django.urls import path
from . import views

app_name = 'hosting'

urlpatterns = [

    path('', views.DashboardView.as_view(), name='hosting_dashboard'),
    path('chart-data/', views.ChartDataView.as_view(), name='chart_data'),

    path('rooms/', views.room_list, name='room_list'),
    path('rooms/create/', views.room_create, name='room_create'),
    path('rooms/update/<str:room_id>/', views.room_update, name='room_update'),
    path('rooms/delete/<str:room_id>/', views.room_delete, name='room_delete'),
    path('rooms/release/<str:room_id>/', views.room_release, name='room_release'),
    path('rooms/generate-id/', views.generate_room_id_view, name='generate_room_id'),
    path('rooms/<str:room_id>/', views.room_detail, name='room_detail'),
    path('rooms/pdf/<str:room_id>/', views.room_pdf, name='room_pdf'),

    path('admissions/', views.admission_list, name='admission_list'),
    path('admissions/create/', views.admission_create, name='admission_create'),
    path('admissions/<int:admission_id>/update/', views.admission_update, name='admission_update'),
    path('admissions/<int:admission_id>/delete/', views.admission_delete, name='admission_delete'),
    path('admissions/<int:admission_id>/detail/', views.admission_detail, name='admission_detail'),
    path('admissions/pdf/<int:admission_id>/', views.admission_pdf, name='admission_pdf'),

    path('beds/', views.bed_list, name='bed_list'),
    path('beds/create/', views.bed_create, name='bed_create'),
    path('beds/<str:bed_id>/update/', views.bed_update, name='bed_update'),
    path('beds/<str:bed_id>/delete/', views.bed_delete, name='bed_delete'),
    path('beds/<str:bed_id>/release/', views.bed_release, name='bed_release'),
    path('beds/<str:bed_id>/detail/', views.bed_detail, name='bed_detail'),
    path('beds/generate-id/', views.generate_bed_id_view, name='generate_bed_id'),
    path('beds/<str:bed_id>/pdf/', views.bed_pdf, name='bed_pdf'),
    
    # Résumé patient hébergement
    path('patient-summary/', views.patient_hosting_summary, name='patient_hosting_summary'),
    path('patient/<int:patient_id>/create-invoice/', views.create_hosting_invoice, name='create_hosting_invoice'),

    path('reservations/', views.reservation_list, name='reservation_list'),
    path('reservations/create/', views.reservation_create, name='reservation_create'),
    path('reservations/<int:reservation_id>/update/', views.reservation_update, name='reservation_update'),
    path('reservations/<int:reservation_id>/delete/', views.reservation_delete, name='reservation_delete'),
    path('reservations/<int:reservation_id>/details/', views.reservation_details, name='reservation_details'),
    path('reservations/<int:reservation_id>/confirm/', views.confirm_reservation, name='confirm_reservation'),
    path('reservations/planning/', views.reservation_planning, name='reservation_planning'), 
    path('reservations/get_calendar_events/', views.get_calendar_events, name='get_calendar_events'),  
    path('reservations/pdf/<int:reservation_id>/', views.reservation_pdf, name='reservation_pdf'), 
    # Companion URLs
    path('companions/', views.companion_list, name='companion_list'),
    path('companions/create/', views.companion_create, name='companion_create'),
    path('companions/<int:companion_id>/update/', views.companion_update, name='companion_update'),
    path('companions/<int:companion_id>/delete/', views.companion_delete, name='companion_delete'),
    path('companions/<int:companion_id>/details/', views.companion_details, name='companion_details'),
    path('configuration/', views.hosting_configuration, name='hosting_configuration'), 

]