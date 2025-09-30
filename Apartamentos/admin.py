from django.contrib import admin
from .models import Apartamento

@admin.register(Apartamento)
class ApartamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero', 'torre', 'propietario', 'ocupantes', 'is_active', 'creado')
    list_filter = ('torre', 'is_active')
    search_fields = ('numero', 'torre', 'propietario__correo', 'propietario__nombres')
    ordering = ('numero',)
    readonly_fields = ('creado', 'modificado')