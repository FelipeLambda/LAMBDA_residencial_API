# Django
from django.conf import settings
from django.db import models
from django.utils import timezone

# Project
from Base.models import BaseModel

class PQRS(BaseModel):
    TYPE_PETITION = 'PETITION'
    TYPE_COMPLAINT = 'COMPLAINT'
    TYPE_CLAIM = 'CLAIM'
    TYPE_SUGGESTION = 'SUGGESTION'
    TYPE_CHOICES = [
        (TYPE_PETITION, 'Petición'),
        (TYPE_COMPLAINT, 'Queja'),
        (TYPE_CLAIM, 'Reclamo'),
        (TYPE_SUGGESTION, 'Sugerencia'),
    ]

    STATUS_OPEN = 'OPEN'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_RESOLVED = 'RESOLVED'
    STATUS_CLOSED = 'CLOSED'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Abierto'),
        (STATUS_IN_PROGRESS, 'En progreso'),
        (STATUS_RESOLVED, 'Resuelto'),
        (STATUS_CLOSED, 'Cerrado'),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='pqrs', verbose_name='Remitente')
    apartamento = models.ForeignKey('Apartamentos.Apartamento', on_delete=models.SET_NULL, null=True, blank=True, related_name='pqrs', verbose_name='Apartamento relacionado')
    tipo = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Tipo')
    asunto = models.CharField(max_length=200, verbose_name='Asunto')
    descripcion = models.TextField(verbose_name='Descripción')
    estado = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN, verbose_name='Estado')
    respuesta = models.TextField(blank=True, null=True, verbose_name='Respuesta del administrador')
    respondido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='pqrs_respondidos', verbose_name='Respondido por')
    fecha_respuesta = models.DateTimeField(blank=True, null=True, verbose_name='Fecha respuesta')

    class Meta:
        db_table = 'pqrs'
        verbose_name = 'PQRS'
        verbose_name_plural = 'PQRS'
        ordering = ['-creado']
        permissions = (
        ('respond_pqrs', 'Puede responder y cerrar PQRS'),
        ('view_pqrs_all', 'Puede ver todas las PQRS'),
    )

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.asunto[:60]}"

    def add_response(self, texto, responder):
        self.respuesta = texto
        self.respondido_por = responder
        self.fecha_respuesta = timezone.now()
        self.estado = self.STATUS_RESOLVED
        self.save()