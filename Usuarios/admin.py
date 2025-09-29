from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

Usuario = get_user_model()

@admin.register(Usuario)
class UsuarioAdmin(DjangoUserAdmin):
    
    # Configuración básica de admin para el usuario personalizado.
    model = Usuario

    list_display = ('id', 'correo', 'nombres', 'apellidos', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('correo', 'nombres', 'apellidos')
    ordering = ('correo',)

    fieldsets = (
        (None, {'fields': ('correo', 'password')}),
        (_('Personal info'), {'fields': ('nombres', 'apellidos')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'creado', 'modificado')}),
    )

    readonly_fields = ('creado', 'modificado')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('correo', 'nombres', 'apellidos', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )