from django.db import models
from django.conf import settings
from Base.models import BaseModel
from django.utils import timezone

class Payment(BaseModel):
    STATUS_PENDING = 'PENDING'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_FAILED = 'FAILED'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendiente'),
        (STATUS_COMPLETED, 'Completado'),
        (STATUS_FAILED, 'Fallido'),
    ]

    apartamento = models.ForeignKey('Apartments.Apartamento', on_delete=models.SET_NULL, null=True, blank=True, related_name='pagos', verbose_name='Apartamento')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='pagos', verbose_name='Usuario')
    periodo = models.CharField(max_length=30, blank=True, null=True, verbose_name='Periodo (ej. 2025-08)')
    monto = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Monto')
    metodo = models.CharField(max_length=50, verbose_name='Método de pago', help_text='Ej: transferencia, efectivo, PSE')
    referencia = models.CharField(max_length=200, blank=True, null=True, verbose_name='Referencia/Transacción')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name='Estado')
    fecha_pago = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de pago')
    nota = models.TextField(blank=True, null=True, verbose_name='Nota / observaciones')

    class Meta:
        db_table = 'payments'
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-creado']
        indexes = [
            models.Index(fields=['apartamento', 'periodo']),
        ]

    def __str__(self):
        return f"Pago {self.id} - {self.monto} - {self.status}"

    def mark_as_paid(self, fecha=None, referencia=None):
        self.status = self.STATUS_COMPLETED
        self.fecha_pago = fecha or timezone.now()
        if referencia:
            self.referencia = referencia
        self.save(update_fields=['status', 'fecha_pago', 'referencia'])