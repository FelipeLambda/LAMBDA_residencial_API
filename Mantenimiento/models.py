import os
from django.conf import settings
from django.db import models
from django.utils import timezone
from Base.models import BaseModel

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


def maintenance_attachment_path(instance, filename):
    return f'maintenance/{instance.maintenance_request.id}/{filename}'


class MaintenanceAttachment(models.Model):
    maintenance_request = models.ForeignKey(MaintenanceRequest, on_delete=models.CASCADE, related_name='attachments', verbose_name='Solicitud de mantenimiento')
    archivo = models.FileField(upload_to=maintenance_attachment_path, verbose_name='Archivo')
    nombre_original = models.CharField(max_length=255, verbose_name='Nombre original')
    tamaño = models.IntegerField(verbose_name='Tamaño (bytes)', help_text='Tamaño en bytes')
    tipo_contenido = models.CharField(max_length=100, blank=True, null=True, verbose_name='Tipo de contenido')
    subido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Subido por')
    subido_en = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de subida')
    es_evidencia_final = models.BooleanField(default=False, verbose_name='Es evidencia final', help_text='Marca si es evidencia de trabajo completado')

    class Meta:
        db_table = 'maintenance_attachments'
        verbose_name = 'Adjunto de mantenimiento'
        verbose_name_plural = 'Adjuntos de mantenimiento'
        ordering = ['-subido_en']

    def __str__(self):
        return f"{self.nombre_original} - Mantenimiento {self.maintenance_request.id}"

    @property
    def extension(self):
        return os.path.splitext(self.nombre_original)[1].lower()

    @property
    def tamaño_mb(self):
        return round(self.tamaño / (1024 * 1024), 2)