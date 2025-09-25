import re
from pathlib import Path
from typing import Optional
from unidecode import unidecode
from django.core.files.storage import default_storage
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


def normalize_path(path: str) -> str:
    
    # Normaliza una ruta/nombre de archivo
    if not path:
        return path
    s = unidecode(path)
    s = s.replace('\\', '/')            
    s = s.replace(' ', '-')
    s = re.sub(r'\.\.+', '', s)        
    s = re.sub(r'[^A-Za-z0-9\-\_\/\.]', '', s)
    s = re.sub(r'\/+', '/', s)
    s = s.lstrip('/')  
    return s


def archivo_upload_to(instance, filename: str) -> str:
    
   # Genera la ruta de almacenamiento para el archivo usando `ruta_archivo` si está definida en la instancia.
    
    base = getattr(instance, 'ruta_archivo', '') or ''
    base = str(base).strip('/')
    full = f"{base}/{filename}" if base else filename
    return normalize_path(full)


class BaseModel(models.Model):
    
    # Modelo base abstracto con campos comunes.
    
    creado = models.DateTimeField(auto_now_add=True, verbose_name=_("Fecha de creación"))
    modificado = models.DateTimeField(auto_now=True, verbose_name=_("Fecha de modificación"))
    is_active = models.BooleanField(default=True, verbose_name=_("Activo"))

    class Meta:
        abstract = True

    def is_active_display(self) -> str:
        return _("Activo") if self.is_active else _("Inactivo")

    def to_dict(self):
        # Útil para debugging.
        return {
            "id": getattr(self, "id", None),
            "creado": self.creado,
            "modificado": self.modificado,
            "is_active": self.is_active,
        }


class Archivo(BaseModel):
    
    # Modelo flexible para almacenar archivos en el storage configurado.

    archivo = models.FileField(upload_to=archivo_upload_to, verbose_name=_("Archivo"), max_length=400)
    ruta_archivo = models.CharField(max_length=300, verbose_name=_("Ruta de archivo"), null=True, blank=True)
    nombre_archivo = models.CharField(max_length=300, verbose_name=_("Nombre del archivo"))
    url_archivo = models.CharField(max_length=1000, verbose_name=_("URL del archivo"), null=True, blank=True)
    archivo_id = models.CharField(max_length=200, verbose_name=_("ID del archivo"), null=True, blank=True)

    class Meta:
        verbose_name = _("Archivo")
        verbose_name_plural = _("Archivos")
        db_table = "base_archivo"
        ordering = ['-creado']

    def __str__(self) -> str:
        return (self.nombre_archivo or (self.url_archivo or str(self.archivo))) or ""

    def get_file_url(self) -> Optional[str]:
        
        # Devuelve URL desde `url_archivo` o desde el storage configurado.

        try:
            if self.url_archivo:
                return self.url_archivo
            if self.archivo and self.archivo.name:
                return default_storage.url(self.archivo.name)
        except Exception:
            return None


# Señales: eliminar archivos físicos de forma segura
@receiver(post_delete, sender=Archivo)
def eliminar_archivo_al_borrar(sender, instance: Archivo, **kwargs):
    try:
        if instance.archivo and instance.archivo.name:
            if default_storage.exists(instance.archivo.name):
                default_storage.delete(instance.archivo.name)
    except Exception:
        # No romper la operación de borrado de la BD por errores de storage.
        pass


@receiver(pre_save, sender=Archivo)
def eliminar_archivo_anterior_al_actualizar(sender, instance: Archivo, **kwargs):
    # Si es nuevo, nada que limpiar
    if not instance.pk:
        return

    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    try:
        old_name = old.archivo.name if old.archivo else None
        new_name = instance.archivo.name if instance.archivo else None
        if old_name and old_name != new_name:
            if default_storage.exists(old_name):
                default_storage.delete(old_name)
    except Exception:
        # proteger contra errores en storage
        pass