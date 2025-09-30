from django.conf import settings
from django.db import models
from django.utils import timezone
from Base.models import BaseModel

class Visit(BaseModel):
    visitante_nombre = models.CharField(max_length=200, verbose_name='Nombre visitante')
    visitante_documento = models.CharField(max_length=100, blank=True, null=True, verbose_name='Documento visitante')
    visitante_telefono = models.CharField(max_length=50, blank=True, null=True, verbose_name='Teléfono')
    placa = models.CharField(max_length=20, blank=True, null=True, verbose_name='Placa vehículo')
    apartamento = models.ForeignKey('Apartamentos.Apartamento', on_delete=models.SET_NULL, null=True, blank=True, related_name='visitas', verbose_name='Apartamento a visitar')
    autoriza_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='visitas_autorizadas', verbose_name='Autorizado por')
    ingresado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='visitas_registradas', verbose_name='Registrado por (portería)')
    fecha_ingreso = models.DateTimeField(default=timezone.now, verbose_name='Fecha ingreso')
    fecha_salida = models.DateTimeField(blank=True, null=True, verbose_name='Fecha salida')
    motivo = models.CharField(max_length=255, blank=True, null=True, verbose_name='Motivo')
    autorizado = models.BooleanField(default=False, verbose_name='Autorizado')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')

    class Meta:
        db_table = 'visits'
        verbose_name = 'Visita'
        verbose_name_plural = 'Visitas'
        ordering = ['-fecha_ingreso']
        permissions = (
        ('authorize_visit', 'Puede autorizar visitas'),
        ('view_visits_all', 'Puede ver todas las visitas'),
    )

    def __str__(self):
        return f"{self.visitante_nombre} -> Apt {self.apartamento_id if self.apartamento_id else 'N/A'} ({self.fecha_ingreso.date()})"