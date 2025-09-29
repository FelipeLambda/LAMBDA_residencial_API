from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import PQRS
from .serializers import PqrsSerializer
from Usuarios.permissions import PQRSOwnerOrManager

class PqrsListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Filtrar PQRS según permisos
        if request.user.has_perm('Pqrs.view_pqrs_all'):
            # Admin puede ver todas las PQRS
            qs = PQRS.objects.all()
        else:
            # Usuario normal solo ve sus propias PQRS
            qs = PQRS.objects.filter(usuario=request.user)

        serializer = PqrsSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PqrsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pqrs = serializer.save(usuario=request.user)
        return Response(PqrsSerializer(pqrs).data, status=status.HTTP_201_CREATED)


class PqrsDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, PQRSOwnerOrManager]

    def get(self, request, pk):
        pqrs = get_object_or_404(PQRS, pk=pk)
        self.check_object_permissions(request, pqrs)
        return Response(PqrsSerializer(pqrs).data)

    def put(self, request, pk):
        pqrs = get_object_or_404(PQRS, pk=pk)

        # Solo admin puede responder/actualizar PQRS
        if not request.user.has_perm('Pqrs.respond_pqrs'):
            return Response({'detail': 'No tiene permiso para responder/actualizar PQRS.'},
                            status=status.HTTP_403_FORBIDDEN)

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