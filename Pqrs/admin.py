from django.contrib import admin
from .models import PQRS

@admin.register(PQRS)
class PqrsAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'asunto', 'usuario', 'estado', 'creado')
    list_filter = ('tipo', 'estado')
    search_fields = ('asunto', 'descripcion', 'usuario__correo')
    ordering = ('-creado',)
    readonly_fields = ('creado', 'modificado', 'fecha_respuesta')