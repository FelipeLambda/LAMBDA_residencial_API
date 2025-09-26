from django.contrib import admin
from .models import Visit

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('id', 'visitante_nombre', 'apartamento', 'autorizado', 'ingresado_por', 'fecha_ingreso')
    list_filter = ('autorizado',)
    search_fields = ('visitante_nombre', 'placa', 'apartamento__numero', 'ingresado_por__correo')
    ordering = ('-fecha_ingreso',)
    readonly_fields = ('creado', 'modificado')