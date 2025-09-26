from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import PQRS
from .serializers import PqrsSerializer

class PqrsListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = PQRS.objects.all()
        if not request.user.has_perm('Pqrs.view_pqrs_all'):
            qs = qs.filter(usuario=request.user)
        serializer = PqrsSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PqrsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pqrs = serializer.save(usuario=request.user)
        return Response(PqrsSerializer(pqrs).data, status=status.HTTP_201_CREATED)


class PqrsDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        item = get_object_or_404(PQRS, pk=pk)
        # Si no tiene permiso para ver todas, sólo ve la suya
        if not request.user.has_perm('Pqrs.view_pqrs_all') and item.usuario != request.user:
            return Response({'detail': 'No tiene permiso.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(PqrsSerializer(item).data)

    def put(self, request, pk):
        item = get_object_or_404(PQRS, pk=pk)
        if not request.user.has_perm('Pqrs.respond_pqrs'):
            return Response({'detail': 'No tiene permiso para responder/actualizar PQRS.'},
                            status=status.HTTP_403_FORBIDDEN)
        respuesta = request.data.get('respuesta', None)
        estado = request.data.get('estado', None)
        if respuesta:
            item.respuesta = respuesta
            item.respondido_por = request.user
            item.fecha_respuesta = timezone.now()
        if estado:
            item.estado = estado
        item.save()
        return Response(PqrsSerializer(item).data)