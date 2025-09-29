from django.db import models
from django.conf import settings

class CommonArea(models.Model):
    
    # Áreas comunes disponibles para reservar (salón social, gimnasio, parqueadero, etc.)
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    capacidad = models.PositiveIntegerField(default=1, verbose_name="Capacidad (opcional)")

    class Meta:
        db_table = 'common_areas'
        verbose_name = 'Área común'
        verbose_name_plural = 'Áreas comunes'

    def __str__(self):
        return self.nombre.title()


class Reservation(models.Model):
    
    # Reserva de un área común por un apartamento/residente.
    STATUS_PENDING = 'PENDING'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendiente'),
        (STATUS_APPROVED, 'Aprobada'),
        (STATUS_REJECTED, 'Rechazada'),
        (STATUS_CANCELLED, 'Cancelada'),
    ]

    apartamento = models.ForeignKey('Apartamentos.Apartamento', on_delete=models.SET_NULL, null=True, blank=True, related_name='reservas', verbose_name='Apartamento')
    area = models.ForeignKey(CommonArea, on_delete=models.PROTECT, related_name='reservas', verbose_name='Área común')
    fecha_inicio = models.DateTimeField(verbose_name='Fecha y hora inicio')
    fecha_fin = models.DateTimeField(verbose_name='Fecha y hora fin')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='reservas_creadas')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservas_aprobadas')
    creado = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    modificado = models.DateTimeField(auto_now=True, verbose_name='Fecha de modificación')
    notas = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'reservations'
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-creado']
        permissions = (
        ('approve_reserva', 'Puede aprobar o rechazar reservas'),
        ('view_reserva_all', 'Puede ver todas las reservas'),
    )

    def __str__(self):
        return f"{self.area} - {self.fecha_inicio} to {self.fecha_fin} ({self.status})"

    def overlaps(self, other_start, other_end):
        # Retorna True si se solapa con el rango
        return not (self.fecha_fin <= other_start or self.fecha_inicio >= other_end)