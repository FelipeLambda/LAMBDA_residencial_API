from functools import wraps
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response


def permission_required(permission_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response(
                    {'detail': 'Autenticación requerida.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            if not request.user.has_perm(permission_name):
                return Response(
                    {'detail': f'No tiene permiso: {permission_name}'},
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_func(self, request, *args, **kwargs)
        return wrapper
    return decorator


def superuser_required(view_func):

    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Autenticación requerida.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not request.user.is_superuser:
            return Response(
                {'detail': 'Requiere privilegios de superusuario.'},
                status=status.HTTP_403_FORBIDDEN
            )

        return view_func(self, request, *args, **kwargs)
    return wrapper


def staff_required(view_func):
 
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Autenticación requerida.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not request.user.is_staff:
            return Response(
                {'detail': 'Requiere privilegios de staff.'},
                status=status.HTTP_403_FORBIDDEN
            )

        return view_func(self, request, *args, **kwargs)
    return wrapper


def log_request(view_func):
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else 'Anonymous'
        method = request.method
        path = request.path
        query_params = dict(request.query_params) if hasattr(request, 'query_params') else {}

        print(f"[REQUEST] {method} {path} | User: {user} | Params: {query_params}")

        response = view_func(self, request, *args, **kwargs)

        status_code = getattr(response, 'status_code', 'N/A')
        print(f"[RESPONSE] {method} {path} | Status: {status_code}")

        return response
    return wrapper


def validate_owner_or_admin(owner_field='propietario'):

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response(
                    {'detail': 'Autenticación requerida.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Superusuarios siempre tienen acceso
            if request.user.is_superuser:
                return view_func(self, request, *args, **kwargs)

            # Obtener el objeto si existe pk
            pk = kwargs.get('pk')
            if pk and hasattr(self, 'get_object'):
                obj = self.get_object()

                # Verificar propiedad
                if hasattr(obj, owner_field):
                    owner = getattr(obj, owner_field)
                    if owner == request.user:
                        return view_func(self, request, *args, **kwargs)

                # Verificar propiedad a través de apartamento
                if hasattr(obj, 'apartamento') and hasattr(obj.apartamento, 'propietario'):
                    if obj.apartamento.propietario == request.user:
                        return view_func(self, request, *args, **kwargs)

                return Response(
                    {'detail': 'No tiene permiso para acceder a este recurso.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_func(self, request, *args, **kwargs)
        return wrapper
    return decorator


def rate_limit_request(max_requests=100, time_window=60):

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            # Se Implementara lógica de rate limiting con cache
            # Por ahora solo retorna la vista sin restricciones
            return view_func(self, request, *args, **kwargs)
        return wrapper
    return decorator


def validate_request_data(*required_fields):

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            missing_fields = []

            for field in required_fields:
                if field not in request.data:
                    missing_fields.append(field)

            if missing_fields:
                return Response(
                    {'detail': f'Campos requeridos faltantes: {", ".join(missing_fields)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return view_func(self, request, *args, **kwargs)
        return wrapper
    return decorator
