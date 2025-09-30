from rest_framework.pagination import LimitOffsetPagination

class ApartamentosPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100


class ReservasPagination(LimitOffsetPagination):
    default_limit = 15
    max_limit = 100


class PagosPagination(LimitOffsetPagination):
    default_limit = 25
    max_limit = 200


class PqrsPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100


class VisitasPagination(LimitOffsetPagination):
    default_limit = 30
    max_limit = 200


class MantenimientoPagination(LimitOffsetPagination):
    default_limit = 15
    max_limit = 100


class UsuariosPagination(LimitOffsetPagination):
    default_limit = 50
    max_limit = 200
