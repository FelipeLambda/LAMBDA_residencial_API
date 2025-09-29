from django.db import models
from django.conf import settings
from Base.models import BaseModel

class Apartamento(BaseModel):
    numero = models.CharField(max_length=20, verbose_name='Número', db_index=True)
    torre = models.CharField(max_length=50, blank=True, null=True, verbose_name='Torre / Bloque')
    piso = models.IntegerField(blank=True, null=True, verbose_name='Piso')
    tipo = models.CharField(max_length=50, blank=True, null=True, verbose_name='Tipo (ej. 2 habitaciones)')
    area_m2 = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, verbose_name='Área (m2)')
    propietario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='apartamentos', verbose_name='Propietario/Residente')
    ocupantes = models.PositiveIntegerField(default=1, verbose_name='Número de ocupantes')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')

    class Meta:
        db_table = 'apartamentos'
        verbose_name = 'Apartamento'
        verbose_name_plural = 'Apartamentos'
        ordering = ['numero']
        permissions = (
        ('manage_apartamentos', 'Puede gestionar apartamentos'),
    )

    def __str__(self):
        return f"Apt. {self.numero} {(' - ' + self.torre) if self.torre else ''}".strip().title()