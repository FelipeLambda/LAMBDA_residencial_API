from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

ROLE_DEFINITIONS = {
    'Administrador': [
        'Users.administrar_modulos',
        'Reservations.approve_reserva',
        'Reservations.view_reserva_all',
        'Payments.mark_pago',
        'Payments.view_pago_all',
        'Pqrs.respond_pqrs',
        'Visits.authorize_visit',
        'Maintenance.assign_maintenance',
        'Maintenance.complete_maintenance',
        'Apartments.manage_apartamentos',
    ],
    'Staff': [
        'Reservations.view_reserva_all',
        'Payments.view_pago_all',
        'Pqrs.view_pqrs_all',
        'Visits.view_visits_all',
        'Maintenance.view_maintenance_all',
    ]
}

class Command(BaseCommand):
    help = 'Crea/actualiza grupos y asigna permisos según ROLE_DEFINITIONS.'

    def handle(self, *args, **options):
        for role_name, perm_list in ROLE_DEFINITIONS.items():
            group, _ = Group.objects.get_or_create(name=role_name)
            perms_to_assign = []
            for full_codename in perm_list:
                try:
                    app_label, codename = full_codename.split('.', 1)
                except ValueError:
                    self.stdout.write(self.style.WARNING(f"Formato inválido: {full_codename}"))
                    continue
                perm = Permission.objects.filter(
                    content_type__app_label__iexact=app_label,
                    codename=codename
                ).first()
                if not perm:
                    self.stdout.write(self.style.WARNING(f"Permiso no encontrado: {full_codename}"))
                    continue
                perms_to_assign.append(perm)
            group.permissions.set(perms_to_assign)
            group.save()
            self.stdout.write(self.style.SUCCESS(f'Grupo \"{role_name}\" actualizado. Permisos: {len(perms_to_assign)}'))
