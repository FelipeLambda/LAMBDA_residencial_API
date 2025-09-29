from rest_framework.permissions import BasePermission


class HasCustomPermission(BasePermission):
    
    # Permiso base para validar permisos personalizados de Django.
    required_permission = None

    def has_permission(self, request, view):
        if not self.required_permission:
            return False
        return request.user and request.user.has_perm(self.required_permission)


class IsOwnerOrHasPermission(BasePermission):

    # Permite acceso si el usuario es propietario del objeto o tiene el permiso específico.
    view_all_permission = None
    owner_field = 'propietario' 

    def has_permission(self, request, view):
        # Permitir acceso básico a usuarios autenticados
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Superusuarios siempre tienen acceso
        if request.user.is_superuser:
            return True

        # Si tiene permiso para ver todos, permitir
        if self.view_all_permission and request.user.has_perm(self.view_all_permission):
            return True

        # Verificar si es propietario del objeto
        if hasattr(obj, self.owner_field):
            owner = getattr(obj, self.owner_field)
            return owner == request.user

        # Verificar si es propietario a través de apartamento
        if hasattr(obj, 'apartamento') and hasattr(obj.apartamento, 'propietario'):
            return obj.apartamento.propietario == request.user

        return False

class CanManageApartments(HasCustomPermission):
    required_permission = 'Apartamentos.manage_apartamentos'


class CanApproveReservations(HasCustomPermission):
    required_permission = 'Reservas.approve_reserva'


class CanMarkPayments(HasCustomPermission):
    required_permission = 'Pagos.mark_pago'

class ReservationOwnerOrManager(IsOwnerOrHasPermission):
    #Propietario de la reserva o administrador con permisos.
    view_all_permission = 'Reservas.view_reserva_all'
    owner_field = 'created_by'


class PaymentOwnerOrManager(IsOwnerOrHasPermission):
    #Propietario del apartamento o administrador con permisos.
    view_all_permission = 'Pagos.view_pago_all'


class MaintenanceOwnerOrManager(IsOwnerOrHasPermission):
    #Propietario del apartamento o administrador con permisos.
    view_all_permission = 'Mantenimiento.view_maintenance_all'


class PQRSOwnerOrManager(IsOwnerOrHasPermission):
    #Propietario del apartamento o administrador con permisos.
    view_all_permission = 'Pqrs.view_pqrs_all'


class VisitOwnerOrManager(IsOwnerOrHasPermission):
    #Propietario del apartamento o administrador con permisos.
    view_all_permission = 'Visitas.view_visits_all'


class ApartmentOwnerOrManager(IsOwnerOrHasPermission):
    # Propietario del apartamento o administrador con permisos.
    view_all_permission = 'Apartamentos.manage_apartamentos'
    owner_field = 'propietario'


class CanCreateForOwnApartment(BasePermission):

    # Permite crear objetos solo para apartamentos del usuario.
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

            # verificar que tenga apartamento
        if request.method in ['POST', 'PUT', 'PATCH']:
            # El usuario debe tener al menos un apartamento
            return hasattr(request.user, 'apartamentos') and request.user.apartamentos.exists()

        return True
