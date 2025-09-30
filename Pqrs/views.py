from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from Base.views import PqrsPagination
from LAMBDA_residencial_API.decorators import permission_required
from .models import PQRS
from .serializers import PqrsSerializer

class PqrsListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PqrsSerializer
    pagination_class = PqrsPagination

    def get_queryset(self):
        # Filtrar PQRS según permisos
        if self.request.user.has_perm('Pqrs.view_pqrs_all'):
            # Admin puede ver todas las PQRS
            return PQRS.objects.all()
        else:
            # Usuario normal solo ve sus propias PQRS
            return PQRS.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class PqrsDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        pqrs = get_object_or_404(PQRS, pk=pk)

        # Permitir acceso si es propietario o tiene permiso para ver todas
        if pqrs.usuario != request.user and not request.user.has_perm('Pqrs.view_pqrs_all'):
            return Response({'detail': 'No tiene permiso para ver esta PQRS.'},
                            status=status.HTTP_403_FORBIDDEN)

        return Response(PqrsSerializer(pqrs).data)

    @permission_required('Pqrs.respond_pqrs')
    def put(self, request, pk):
        pqrs = get_object_or_404(PQRS, pk=pk)

        respuesta = request.data.get('respuesta', None)
        estado = request.data.get('estado', None)

        if respuesta:
            pqrs.respuesta = respuesta
            pqrs.respondido_por = request.user
            pqrs.fecha_respuesta = timezone.now()

        if estado:
            pqrs.estado = estado

        pqrs.save()
        return Response(PqrsSerializer(pqrs).data)