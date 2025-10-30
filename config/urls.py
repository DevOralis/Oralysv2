from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('apps.dashboard.urls')),
    path('', include('apps.home.urls')),
    path('parcauto/', include('apps.parcauto.urls')),
    path('restauration/', include('apps.Restauration.urls')),
    path('recruitment/', include('apps.recruitment.urls')),
    path('hr/', include('apps.hr.urls')), 
    path('formation/', include('apps.formation.urls')),
    path('patient/', include('apps.patient.urls')),
    path('pharmacy/', include('apps.pharmacy.urls')), 
    path('purchases/', include('apps.purchases.urls')),
    path('inventory/', include('apps.inventory.urls')), 
    path('therapeutic_activities/', include('apps.therapeutic_activities.urls')),
    path('hosting/', include('apps.hosting.urls', namespace='hosting')),
    path('maintenance/', include('apps.maintenance.urls', namespace='maintenance')),
    path('demandes/', include('apps.demandes.urls', namespace='demandes')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
