from django.contrib import admin
from .models import TypeMaintenance, Convention


@admin.register(TypeMaintenance)
class TypeMaintenanceAdmin(admin.ModelAdmin):
    list_display = ('code', 'libelle')
    search_fields = ('code', 'libelle')



@admin.register(Convention)
class ConventionAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'type_convention', 'type_maintenance', 
                   'date_debut', 'date_fin', 'cout_mensuel', 'active')
    list_filter = ('type_convention', 'active', 'type_maintenance', 'date_debut')
    search_fields = ('supplier__nom', 'description')
    date_hierarchy = 'date_debut'
    list_editable = ('active',)
    fieldsets = (
        (None, {
            'fields': ('supplier', 'type_convention', 'type_maintenance')
        }),
        ('Dates', {
            'fields': ('date_debut', 'date_fin')
        }),
        ('Autres informations', {
            'fields': ('description', 'cout_mensuel', 'active')
        }),
    )

