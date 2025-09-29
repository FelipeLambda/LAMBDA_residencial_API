from django.contrib import admin
from .models import MaintenanceRequest

@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'area', 'solicitado_por', 'asignado_a', 'estado', 'fecha_programada', 'creado')
    list_filter = ('estado', 'area', 'notificar_residentes')
    search_fields = ('descripcion', 'solicitado_por__correo', 'asignado_a__correo')
    ordering = ('-creado',)
    readonly_fields = ('creado', 'modificado', 'fecha_finalizado')