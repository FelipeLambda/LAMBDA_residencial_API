from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'apartamento', 'usuario', 'periodo', 'monto', 'status', 'creado')
    list_filter = ('status', 'metodo')
    search_fields = ('referencia', 'apartamento__numero', 'usuario__correo')
    ordering = ('-creado',)
    readonly_fields = ('creado', 'modificado')