from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, correo, nombres, apellidos, password=None, **extra_fields):
        if not correo:
            raise ValueError('El usuario debe tener un correo electrónico.')
        if not nombres:
            raise ValueError('El usuario debe tener un nombre.')
        if not apellidos:
            raise ValueError('El usuario debe tener un apellido.')

        correo = self.normalize_email(correo)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        user = self.model(
            correo=correo,
            nombres=nombres,
            apellidos=apellidos,
            **extra_fields
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, correo, nombres, apellidos, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        return self.create_user(correo, nombres, apellidos, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    correo = models.EmailField(verbose_name='Correo', max_length=255, unique=True)
    nombres = models.CharField(max_length=30, verbose_name='Nombres')
    apellidos = models.CharField(max_length=30, verbose_name='Apellidos')
    creado = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    modificado = models.DateTimeField(auto_now=True, verbose_name="Fecha de modificación")
    # Flags requeridos por Django/admin
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    is_staff = models.BooleanField(default=False, verbose_name='Staff (acceso admin)')
    # Token para recuperación de contraseña
    reset_password_token = models.CharField(max_length=200, blank=True, null=True)
    reset_password_token_expires_at = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombres', 'apellidos']

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        permissions = (
            ('administrar_modulos', 'Puede administrar módulos (permiso global de módulo)'),
            ('aprobar_reservas', 'Puede aprobar reservas'),
            ('gestionar_pagos', 'Puede gestionar pagos'),
        )

    def __str__(self):
        return f"{self.nombres} {self.apellidos}".strip().title()
    def get_full_name(self):
        return f"{self.nombres} {self.apellidos}".strip().title()
    def get_short_name(self):
        return self.nombres.strip().title()

    def create_reset_token(self, hours_valid=1):
        self.reset_password_token = get_random_string(50)
        self.reset_password_token_expires_at = timezone.now() + timedelta(hours=hours_valid)
        self.save(update_fields=['reset_password_token', 'reset_password_token_expires_at'])

    def reset_token_valid(self):
        if not self.reset_password_token_expires_at:
            return False
        return timezone.now() < self.reset_password_token_expires_at
