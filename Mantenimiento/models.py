from django.db import models
from django.conf import settings
from Base.models import BaseModel
from django.utils import timezone

class MaintenanceRequest(BaseModel):
    STATUS_REQUESTED = 'REQUESTED'
    STATUS_SCHEDULED = 'SCHEDULED'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_CHOICES = [
        (STATUS_REQUESTED, 'Solicitado'),
        (STATUS_SCHEDULED, 'Programado'),
        (STATUS_IN_PROGRESS, 'En progreso'),
        (STATUS_COMPLETED, 'Completado'),
        (STATUS_CANCELLED, 'Cancelado'),
    ]

    area = models.ForeignKey('Reservas.CommonArea', on_delete=models.SET_NULL, null=True, blank=True, related_name='mantenimientos', verbose_name='Área común (si aplica)')
    descripcion = models.TextField(verbose_name='Descripción del problema')
    solicitado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='mantenimientos_solicitados', verbose_name='Solicitado por')
    asignado_a = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='mantenimientos_asignados', verbose_name='Asignado a')
    fecha_programada = models.DateTimeField(blank=True, null=True, verbose_name='Fecha programada')
    fecha_finalizado = models.DateTimeField(blank=True, null=True, verbose_name='Fecha finalizado')
    costo_estimado = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name='Costo estimado')
    costo_final = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name='Costo final')
    estado = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_REQUESTED, verbose_name='Estado')
    notificar_residentes = models.BooleanField(default=True, verbose_name='Notificar a residentes')
    comentario_admin = models.TextField(blank=True, null=True, verbose_name='Comentario administración')

    class Meta:
        db_table = 'maintenance_requests'
        verbose_name = 'Solicitud de mantenimiento'
        verbose_name_plural = 'Solicitudes de mantenimiento'
        ordering = ['-creado']
        permissions = (
        ('assign_maintenance', 'Puede asignar solicitudes de mantenimiento'),
        ('complete_maintenance', 'Puede marcar mantenimiento como completado'),
        ('view_maintenance_all', 'Puede ver todas las solicitudes de mantenimiento'),
    )

    def __str__(self):
        return f"Mantenimiento {self.id} - {self.get_estado_display()}"

    def mark_completed(self, fecha=None, costo_final=None):
        self.estado = self.STATUS_COMPLETED
        self.fecha_finalizado = fecha or timezone.now()
        if costo_final is not None:
            self.costo_final = costo_final
        self.save()