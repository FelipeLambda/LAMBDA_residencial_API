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
    required_permission = 'Apartments.manage_apartamentos'


class CanApproveReservations(HasCustomPermission):
    required_permission = 'Reservations.approve_reserva'


class CanViewAllReservations(HasCustomPermission):
    required_permission = 'Reservations.view_reserva_all'


class CanMarkPayments(HasCustomPermission):
    required_permission = 'Payments.mark_pago'


class CanViewAllPayments(HasCustomPermission):
    required_permission = 'Payments.view_pago_all'


class CanRespondPQRS(HasCustomPermission):
    required_permission = 'Pqrs.respond_pqrs'


class CanViewAllPQRS(HasCustomPermission):
    required_permission = 'Pqrs.view_pqrs_all'


class CanAuthorizeVisits(HasCustomPermission):
    required_permission = 'Visits.authorize_visit'


class CanViewAllVisits(HasCustomPermission):
    required_permission = 'Visits.view_visits_all'


class CanAssignMaintenance(HasCustomPermission):
    required_permission = 'Maintenance.assign_maintenance'


class CanCompleteMaintenance(HasCustomPermission):
    required_permission = 'Maintenance.complete_maintenance'


class CanViewAllMaintenance(HasCustomPermission):
    required_permission = 'Maintenance.view_maintenance_all'

class ReservationOwnerOrManager(IsOwnerOrHasPermission):
    #Propietario de la reserva o administrador con permisos.
    view_all_permission = 'Reservations.view_reserva_all'
    owner_field = 'created_by'


class PaymentOwnerOrManager(IsOwnerOrHasPermission):
    #Propietario del apartamento o administrador con permisos.
    view_all_permission = 'Payments.view_pago_all'


class MaintenanceOwnerOrManager(IsOwnerOrHasPermission):
    #Propietario del apartamento o administrador con permisos.
    view_all_permission = 'Maintenance.view_maintenance_all'


class PQRSOwnerOrManager(IsOwnerOrHasPermission):
    #Propietario del apartamento o administrador con permisos.
    view_all_permission = 'Pqrs.view_pqrs_all'


class VisitOwnerOrManager(IsOwnerOrHasPermission):
    #Propietario del apartamento o administrador con permisos.
    view_all_permission = 'Visits.view_visits_all'


class ApartmentOwnerOrManager(IsOwnerOrHasPermission):
    # Propietario del apartamento o administrador con permisos.
    view_all_permission = 'Apartments.manage_apartamentos'
    owner_field = 'propietario'

class IsAdminOrOwner(BasePermission):
    
    # Permite acceso a administradores o propietarios del objeto.
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Superusuarios y staff siempre tienen acceso
        if request.user.is_superuser or request.user.is_staff:
            return True

        # Verificar si es propietario
        if hasattr(obj, 'propietario'):
            return obj.propietario == request.user

        # Para objetos relacionados a apartamentos
        if hasattr(obj, 'apartamento') and hasattr(obj.apartamento, 'propietario'):
            return obj.apartamento.propietario == request.user

        return False


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
