from django.contrib import admin
from .models import CommonArea, Reservation

@admin.register(CommonArea)
class CommonAreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'capacidad')
    search_fields = ('nombre',)
    ordering = ('nombre',)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'area', 'apartamento', 'fecha_inicio', 'fecha_fin', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'area')
    search_fields = ('area__nombre', 'apartamento__numero', 'created_by__correo')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')